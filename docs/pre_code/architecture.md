# Accounting System Architecture

## System Overview

A fully integrated accounting system for Iranian SMEs and personal finance management, with Persian localization, 6-level chart of accounts, multi-currency support, and three access modes (web browser, Windows desktop, mobile app).

## Technology Stack

### Backend (FastAPI)
- **Language**: Python 3.12+
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL 16 with TimescaleDB
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT + OAuth2 with role-based access control
- **Security**: AES-256 encryption, audit logging middleware

### Frontend (Web Browser)
- **Framework**: React 18 + TypeScript
- **Styling**: Material UI with Persian RTL themes
- **Calendar**: Solar Hijri calendar component
- **Charts**: Chart.js with Persian number formatters
- **Build**: Vite 6 with React SSR support

### Windows Desktop Application
- **Framework**: Electron 30 with Rust (Tauri) for native IPC
- **UI**: React + TypeScript (same frontend codebase)
- **Native**: Win32 API for file system operations
- **Storage**: Windows registry + JSON file backup

### Mobile Application
- **Framework**: React Native 0.72 with TypeScript
- **UI**: React Native components with Material Design
- **Navigation**: React Navigation with tab-based layout
- **Device**: iOS 15+ / Android 11+

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│             Mobile App / Windows            │
│  (React Native / Electron)                  │
├─────────────────────────────────────────────┤
│              API Gateway (Nginx)            │
├─────────────────────────────────────────────┤
│            Backend API (FastAPI)             │
│  ┌─────────────────────────────────────────┐ │
│  │  Controllers (V1, V2, V3)              │ │
│  │  Repositories (Postgres)               │ │
│  │  Services (Business Logic)             │ │
│  │  Middleware (Auth, Rate Limit)          │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │  Database (PostgreSQL + TimescaleDB)    │ │
│  │  Cache (Redis)  │  File Storage         │ │
│  └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│        Shared: DB Schema, Config, Models   │
└─────────────────────────────────────────────┘
```

## Database Schema

### Core Tables

```sql
-- 6-Level Chart of Accounts
accounts (
    id UUID PK,
    code VARCHAR(3) NOT NULL,        -- Level 1 (Main Group)
    name_fa VARCHAR(100) NOT NULL,    -- اینام گروه اصلی
    name_en VARCHAR(100),             -- اینام انگلیسی
    parent_id UUID REFERENCES accounts(id),  -- هدر سطن
    level INTEGER NOT NULL,          -- سطح: 1=ریشه 2=زیرگروه 3=گردر 4=زیردسته 5=تفصیل1 6=تفصیل2
    type VARCHAR(1) NOT NULL,        -- T=شناسه, D=مقایسه چپ/راست  -- توضیح گروه
    is_active BOOLEAN DEFAULT true,
    is_memo BOOLEAN DEFAULT false,    -- حساب مکمل
    is_contingent BOOLEAN DEFAULT false, -- حساب قراردادی
    currency_id UUID REFERENCES currencies(id), -- پول واحد پنهان، هر کدوم
    parent_code VARCHAR(3), -- شماره پدر (برای ثبت کابل)
    is_balanced BOOLEAN DEFAULT true,
    position INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

-- Journal Entries
journal_entries (
    id UUID PK,
    voucher_no VARCHAR(15) NOT NULL,  -- شماره وبر
    voucher_type VARCHAR(1) NOT NULL, -- N=عادی C=تصحیح C=بسته
    period VARCHAR(20) NOT NULL,      -- تایم فصلی (مه 2026-یک
    date DATE NOT NULL,               -- تاریخ گرامور
    solar_date DATE,                   -- تاریخ شمسی
    iso_date DATE NOT NULL,
    debit DECIMAL(18,4) NOT NULL,     -- اعتبار (فیلده شمات)
    credit DECIMAL(18,4) NOT NULL,    -- اعتبار (فیلده میانه)
    account_id UUID REFERENCES accounts(id), -- کد حساب چپ/راست
    account_name VARCHAR(100),        -- نام حساب
    counterparty_id UUID REFERENCES clients(id), -- مشتری/مالک
    description_fa TEXT,              -- توضیح فارسی
    description_en TEXT,              -- توضیح انگلیسی
    reference VARCHAR(50),             -- دستورالعمل
    approval_level INTEGER DEFAULT 0,  -- سطح پذیرش: 0=بدون پذیرش 1=مستقل 2=مصاحبه1 3=مصاحبه2 4=مصاحبه3
    is_approved BOOLEAN DEFAULT false,
    is_correction BOOLEAN DEFAULT false, -- واریسی
    is_locked BOOLEAN DEFAULT false,   -- کلوکد
    is_system_generated BOOLEAN DEFAULT false, -- سیستم
    entry_time TIMESTAMPTZ DEFAULT now(), -- زمان پر کردن
    modified_time TIMESTAMPTZ,
    period_end BOOLEAN DEFAULT false,  -- تاریخ بسته شدن
    user_id UUID REFERENCES users(id)
)

-- Ledger Accounts
general_ledgers (
    id UUID PK,
    account_id UUID REFERENCES accounts(id),
    period VARCHAR(20) NOT NULL,
    opening_balance DECIMAL(18,4) NOT NULL,
    closing_balance DECIMAL(18,4),
    debit_amount DECIMAL(18,4),
    credit_amount DECIMAL(18,4),
    net_balance DECIMAL(18,4),
    ledger_type VARCHAR(1) NOT NULL, -- I=راهنمایی، S=وصلات، ...
    is_active BOOLEAN DEFAULT true
)

subsidiary_ledgers (
    id UUID PK,
    account_id UUID REFERENCES accounts(id),
    subsidiary_id UUID REFERENCES subsidiary_accounts(id),
    period VARCHAR(20) NOT NULL,
    amount DECIMAL(18,4),
    balance DECIMAL(18,4)
)

detail_ledgers (
    id UUID PK,
    account_id UUID REFERENCES accounts(id),
    detail_level INTEGER NOT NULL,
    amount DECIMAL(18,4),
    description_fa TEXT,
    period VARCHAR(20) NOT NULL,
    is_final BOOLEAN DEFAULT false
)

-- Clients / Vendors / Banks
clients (
    id UUID PK,
    name VARCHAR(200) NOT NULL,
    name_fa VARCHAR(100),
    type VARCHAR(1) NOT NULL, -- C=عمولی, P=آقایان, S=مشارکت‌کنندگان, B=بنیادها
    tax_id VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    is_active BOOLEAN DEFAULT true
)

currencies (
    id UUID PK,
    code VARCHAR(3) NOT NULL, -- 'IRR', 'USD', 'EUR', 'AED'
    name_fa VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    is_active BOOLEAN DEFAULT true
)

exchange_rates (
    id UUID PK,
    currency_id UUID REFERENCES currencies(id),
    rate DECIMAL(15,10) NOT NULL,
    effective_date DATE NOT NULL,
    rate_type VARCHAR(1) NOT NULL, -- R=رایگان, E=توسط، A=توسط، C=توسط، F=توسط، T=توسط
    created_at TIMESTAMPTZ DEFAULT now()
)

budgets (
    id UUID PK,
    account_id UUID REFERENCES accounts(id),
    period VARCHAR(20) NOT NULL,
    budget_amount DECIMAL(18,4) NOT NULL,
    actual_amount DECIMAL(18,4),
    variance DECIMAL(18,4),
    is_active BOOLEAN DEFAULT true
)

-- Approval Workflows
approval_levels (
    id UUID PK,
    name VARCHAR(20) NOT NULL,        -- پذیرش1، پذیرش2، پذیرش3
    type VARCHAR(1) NOT NULL,         -- N=نرم، A=محرک، R=پایانی
    level INTEGER NOT NULL,            -- سطح
    is_mandatory BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false
)

voucher_approvals (
    id UUID PK,
    voucher_id UUID REFERENCES journal_entries(id),
    level INTEGER NOT NULL,
    status VARCHAR(1) NOT NULL,        -- A=انجام، N=ناقص، P=پیشنهادی
    approved_by UUID REFERENCES users(id),
    approver_date TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    comments TEXT
)

-- Audit Logs
audit_logs (
    id UUID PK,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(30) NOT NULL,
    entity_id UUID,
    entity_name VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent VARCHAR(200),
    timestamp TIMESTAMPTZ DEFAULT now()
)

-- Users & Roles
users (
    id UUID PK,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(20) NOT NULL,         -- ADMIN, ACCOUNTANT, MANAGER, USER
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ,
    failed_login_count INTEGER DEFAULT 0
)

roles (
    id UUID PK,
    name VARCHAR(30) NOT NULL,
    permissions JSONB
)

permissions (
    id UUID PK,
    role_id UUID REFERENCES roles(id),
    resource VARCHAR(50),
    action VARCHAR(10) NOT NULL,
    can_access BOOLEAN DEFAULT true
)

-- Financial Statements
financial_statements (
    id UUID PK,
    type VARCHAR(30) NOT NULL,         -- B=کساد، P=هزینه، C=سود، F=فصلی
    period VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    balance DECIMAL(18,4),
    variance DECIMAL(18,4),
    is_comparative BOOLEAN DEFAULT false,
    is_locked BOOLEAN DEFAULT false
)

-- Invoices
invoices (
    id UUID PK,
    invoice_no VARCHAR(20) NOT NULL,
    client_id UUID REFERENCES clients(id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(18,4) NOT NULL,
    tax_amount DECIMAL(18,4),
    is_approved BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id)
)

-- Budgets
budget_items (
    id UUID PK,
    account_id UUID REFERENCES accounts(id),
    period VARCHAR(20) NOT NULL,
    budget_amount DECIMAL(18,4) NOT NULL,
    is_active BOOLEAN DEFAULT true
)

-- System Config
config (
    id UUID PK,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description VARCHAR(200)
)

-- Backups
backups (
    id UUID PK,
    created_at TIMESTAMPTZ DEFAULT now(),
    size_bytes BIGINT,
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL,
    checksum VARCHAR(64)
)
