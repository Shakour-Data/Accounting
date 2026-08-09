# Accounting System Implementation Plan

## Project Scope
Multi-platform accounting system for Iranian SMEs with Persian localization, 6-level chart of accounts, multi-currency support, three access modes (web, Windows desktop, mobile). Must comply with Iranian Accounting Standards 168 & 169.

## Technology Stack (All Decisions Finalized)

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL 16 + Redis cache
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **Auth**: JWT + RBAC (roles: ADMIN, ACCOUNTANT, MANAGER, USER)
- **Security**: AES-256-GCM encryption per-account, audit logging middleware

### Web Frontend
- **Framework**: React 18 + TypeScript + Vite 6
- **UI Library**: Material UI (MUI) with Persian RTL theme
- **Font**: Vazirmatn
- **Calendar**: Solar Hijri (Jalaali) calendar component
- **Charts**: Chart.js with Persian number formatters
- **Testing**: Jest + React Testing Library

### Windows Desktop
- **Framework**: Electron 30 (shared React/TS codebase with web)
- **IPC**: Native file operations, printing, auto-update
- **Storage**: Local encrypted paths + Windows registry config

### Mobile
- **Framework**: React Native 0.72 + TypeScript
- **Navigation**: React Navigation (tab-based)
- **UI**: React Native components with Material Design
- **Offline**: Background sync queue

### Infrastructure
- **CI/CD**: GitHub Actions (lint, typecheck, test, build)
- **Deployment**: Docker + docker-compose on Linux servers
- **API**: Path-based versioning (/v1/) with OpenAPI 3.0 spec
- **File Storage**: Local path-based with encrypted filename obfuscation

## Implementation Phases

### Phase 1: Core Architecture & Database (Week 1-2)
1. Provision PostgreSQL 16 + Redis
2. Initialize FastAPI project structure
3. Create Alembic migration for complete schema (architecture.md)
4. Implement 6-level Chart of Accounts models + repositories
5. Build JWT + RBAC authentication system
6. Create core V1 API: accounts, journal entries, clients, currencies
7. Add audit logging middleware
8. Configure OpenAPI 3.0 spec generation

### Phase 2: Web Frontend Foundation (Week 3-4)
1. Initialize React 18 + TS + Vite + MUI project
2. Configure RTL theme, Vazirmatn font, Persian number formatters
3. Build Solar Hijri calendar component
4. Implement Chart of Accounts management (tree view, 6-level CRUD)
5. Create Journal Entry form with real-time debit/credit validation
6. Add file attachment upload with encryption

### Phase 3: Windows Desktop App (Week 5)
1. Initialize Electron 30 + React project
2. Configure shared codebase with web frontend
3. Implement native IPC for file operations and printing
4. Build installer with auto-update
5. Verify RTL rendering on Windows

### Phase 4: Mobile App Foundation (Week 6-7)
1. Initialize React Native 0.72 + TS project
2. Configure React Navigation (tab-based)
3. Build core screens: Dashboard, Voucher List, Account Tree
4. Implement offline-first sync with background queue

### Phase 5: Core Accounting Functionality (Week 7-10)
1. Implement Approval Workflow Engine (3 levels, configurable)
2. Build Multi-Currency Exchange Management (USD/EUR/AED/IRR)
3. Develop Journal Validation Engine (debit=credit enforcement)
4. Create Voucher Templates for recurring transactions
5. Add year-end revaluation entry generation

### Phase 6: Reporting & Analysis (Week 11-13)
1. General Ledger report (all 6 levels, PDF/Excel export)
2. Subsidiary Ledger report (customer/supplier/bank details)
3. Detail Ledger report (project/branch/department costs)
4. Financial Statements: Balance Sheet, P&L, Cash Flow
5. Aging Reports for receivables/payables
6. Dashboard with Chart.js visualizations

### Phase 7: Advanced Features (Week 14-16)
1. Budget Management with variance tracking and alerts
2. Iranian Tax Authority export (Saman-e Moo'adian format)
3. Fiscal Period Management (open/close, corrections)
4. Backup/Recovery system (daily dumps + Point-in-Time)

### Phase 8: Polish & Deployment (Week 17-18)
1. RTL/UI polish across all three platforms
2. Performance optimization for 10k+ voucher queries
3. Security audit and penetration testing
4. Prepare Dockerfiles and docker-compose
5. Create Persian user manual
6. Record training video

## Key Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complex 6-level account hierarchy performance | High | Proper indexing, materialized paths, Redis caching |
| Persian RTL across 3 platforms | High | Shared component library, automated RTL testing |
| Iranian tax export format compliance | High | Early integration testing with test environment |
| Approval workflow state machine bugs | High | Comprehensive unit tests, formal state verification |
| Multi-currency rounding/revaluation | Medium | Decimal precision (18,4), test edge cases |

## Validation Plan (from RFB.md Acceptance Criteria)

1. **Standards Compliance**: All calculations verified against Iranian Accounting Standards 168 & 169
2. **Ledger Generation**: Journal, GL, Subsidiary, Detail ledgers at all 6 levels generate error-free
3. **Immutability**: Level-3 approved vouchers locked; only corrective vouchers allowed
4. **Performance**: Report loading < 5 seconds with 10,000 vouchers
5. **Tax Export**: Generated files accepted by Iranian tax authority test system
6. **Localization**: Full Persian RTL, Vazirmatn font, Solar Hijri calendar, Persian numerals
7. **Security**: AES-256-GCM encryption, complete audit log coverage

## Out of Scope (Phase 1)
- Full payroll module (simple salary recording only)
- Inventory and stock management
- Direct bank gateway integration (CSV import only)
- Production and cost accounting module

---

**Plan Status**: Implementation-ready. All technology decisions resolved. Ready for development team execution.