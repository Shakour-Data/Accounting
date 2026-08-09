# Pre-Code Diagrams (Six Levels)

This document contains the six-level diagrammatic specification for the Accounting System, covering UML, BPMN, DFD, and ERD perspectives.

---

## Level 1 – System Context Diagram (C4 Context)

```mermaid
graph TD
    subgraph "External Actors"
        User["Accountant / Manager / Owner"]
        TaxAuth["Iran Tax Authority (Saman-e Moo'adian)"]
        Bank["Bank CSV Exports"]
    end

    System["Accounting System"]

    User -->|Web Browser / Windows App / Mobile App| System
    System -->|Tax Export Files| TaxAuth
    System -->|Import CSV| Bank
```

---

## Level 2 – Container Diagram (C4 Container)

```mermaid
graph TD
    subgraph "User Interfaces"
        WebApp["Web Frontend (React + TS)"]
        WinApp["Windows App (Electron/Tauri)"]
        MobApp["Mobile App (React Native)"]
    end

    subgraph "API Gateway"
        GW["NGINX / Kong"]
    end

    subgraph "Backend Services"
        AuthSvc["Auth Service"]
        LedgerSvc["Ledger Service"]
        VoucherSvc["Voucher Service"]
        ReportSvc["Report Service"]
        CurrencySvc["Currency Service"]
        BudgetSvc["Budget Service"]
        ApprovalSvc["Approval Workflow Service"]
        AuditSvc["Audit Log Service"]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL + TimescaleDB)]
        Redis[(Redis Cache)]
        FS["File Storage (Attachments)"]
    end

    WebApp --> GW
    WinApp --> GW
    MobApp --> GW

    GW --> AuthSvc
    GW --> LedgerSvc
    GW --> VoucherSvc
    GW --> ReportSvc
    GW --> CurrencySvc
    GW --> BudgetSvc
    GW --> ApprovalSvc
    GW --> AuditSvc

    AuthSvc --> PG
    LedgerSvc --> PG
    VoucherSvc --> PG
    ReportSvc --> PG
    CurrencySvc --> PG
    BudgetSvc --> PG
    ApprovalSvc --> PG
    AuditSvc --> PG

    LedgerSvc --> Redis
    VoucherSvc --> FS
```

---

## Level 3 – Component Diagram (C4 Component) – Backend Core

```mermaid
graph TD
    subgraph "Auth Module"
        AuthCtrl["AuthController"]
        UserRepo["UserRepository"]
        RoleRepo["RoleRepository"]
        JwtSvc["JwtService"]
    end

    subgraph "Chart of Accounts Module"
        AccCtrl["AccountController"]
        AccRepo["AccountRepository"]
        AccSvc["AccountService"]
    end

    subgraph "Voucher Module"
        VoucherCtrl["VoucherController"]
        VoucherRepo["VoucherRepository"]
        VoucherSvc["VoucherService"]
        TemplateRepo["VoucherTemplateRepository"]
    end

    subgraph "Approval Workflow Module"
        ApprovalCtrl["ApprovalController"]
        ApprovalRepo["ApprovalRepository"]
        ApprovalSvc["ApprovalService"]
    end

    subgraph "Reporting Module"
        ReportCtrl["ReportController"]
        ReportSvc["ReportService"]
        LedgerRepo["GeneralLedgerRepository"]
        SubLedgerRepo["SubsidiaryLedgerRepository"]
        DetailLedgerRepo["DetailLedgerRepository"]
    end

    subgraph "Currency Module"
        CurrCtrl["CurrencyController"]
        CurrRepo["CurrencyRepository"]
        RateRepo["ExchangeRateRepository"]
        CurrSvc["CurrencyService"]
    end

    subgraph "Budget Module"
        BudCtrl["BudgetController"]
        BudRepo["BudgetRepository"]
        BudSvc["BudgetService"]
    end

    subgraph "Audit Module"
        AuditCtrl["AuditController"]
        AuditRepo["AuditRepository"]
        AuditSvc["AuditService"]
    end
```

---

## Level 4 – Domain Class Diagram (UML)

```mermaid
classDiagram
    class Account {
        +UUID id
        +String code
        +String name_fa
        +String name_en
        +UUID parent_id
        +Int level
        +Char type
        +Boolean is_active
        +Boolean is_memo
        +Boolean is_contingent
        +UUID currency_id
    }

    class JournalEntry {
        +UUID id
        +String voucher_no
        +Char voucher_type
        +String period
        +Date date
        +Date solar_date
        +Decimal debit
        +Decimal credit
        +UUID account_id
        +UUID counterparty_id
        +String description_fa
        +Int approval_level
        +Boolean is_approved
        +Boolean is_correction
        +Boolean is_locked
    }

    class Client {
        +UUID id
        +String name
        +String name_fa
        +Char type
        +String tax_id
        +String phone
        +String email
        +String address
        +Boolean is_active
    }

    class Currency {
        +UUID id
        +String code
        +String name_fa
        +String name_en
        +Boolean is_active
    }

    class ExchangeRate {
        +UUID id
        +UUID currency_id
        +Decimal rate
        +Date effective_date
        +Char rate_type
    }

    class Budget {
        +UUID id
        +UUID account_id
        +String period
        +Decimal budget_amount
        +Decimal actual_amount
        +Decimal variance
        +Boolean is_active
    }

    class ApprovalLevel {
        +UUID id
        +String name
        +Char type
        +Int level
        +Boolean is_mandatory
        +Boolean is_default
    }

    class VoucherApproval {
        +UUID id
        +UUID voucher_id
        +Int level
        +Char status
        +UUID approved_by
        +DateTime approver_date
        +DateTime approved_at
        +String comments
    }

    class AuditLog {
        +UUID id
        +UUID user_id
        +String action
        +String entity_type
        +UUID entity_id
        +String entity_name
        +JSON old_value
        +JSON new_value
        +String ip_address
        +String user_agent
        +DateTime timestamp
    }

    class User {
        +UUID id
        +String username
        +String email
        +String password_hash
        +String full_name
        +Boolean is_active
        +String role
        +Boolean is_verified
        +DateTime created_at
        +DateTime last_login
    }

    Account "1" -- "0..*" Account : parent
    JournalEntry "*" -- "1" Account : account
    JournalEntry "*" -- "0..1" Client : counterparty
    VoucherApproval "*" -- "1" JournalEntry : voucher
    VoucherApproval "*" -- "1" User : approved_by
    Budget "*" -- "1" Account : account
    ExchangeRate "*" -- "1" Currency : currency
    AuditLog "*" -- "1" User : user
```

---

## Level 5 – Sequence Diagram: Voucher Approval Workflow

```mermaid
sequenceDiagram
    actor Accountant
    actor Manager
    participant Frontend
    participant VoucherSvc
    participant ApprovalSvc
    participant DB

    Accountant->>Frontend: Create Voucher (Draft)
    Frontend->>VoucherSvc: POST /vouchers
    VoucherSvc->>DB: INSERT voucher (approval_level=0)
    DB-->>VoucherSvc: voucher_id
    VoucherSvc-->>Frontend: 201 Created

    Accountant->>Frontend: Submit for Approval L1
    Frontend->>ApprovalSvc: POST /approvals/{voucher_id}/submit?level=1
    ApprovalSvc->>DB: UPDATE voucher approval_level=1
    ApprovalSvc->>DB: INSERT voucher_approval (level=1, status='P')
    DB-->>ApprovalSvc: OK
    ApprovalSvc-->>Frontend: 200 OK

    Manager->>Frontend: Review Voucher
    Frontend->>ApprovalSvc: GET /approvals/{voucher_id}
    ApprovalSvc->>DB: SELECT approvals
    DB-->>ApprovalSvc: approval records
    ApprovalSvc-->>Frontend: approval details

    Manager->>Frontend: Approve Level 1
    Frontend->>ApprovalSvc: POST /approvals/{voucher_id}/approve?level=1
    ApprovalSvc->>DB: UPDATE voucher_approval SET status='A', approved_by=manager_id
    ApprovalSvc->>DB: UPDATE voucher approval_level=2
    DB-->>ApprovalSvc: OK
    ApprovalSvc-->>Frontend: 200 OK

    alt Level 2 Mandatory
        Manager->>Frontend: Approve Level 2
        Frontend->>ApprovalSvc: POST /approvals/{voucher_id}/approve?level=2
        ApprovalSvc->>DB: UPDATE voucher_approval SET status='A'
        ApprovalSvc->>DB: UPDATE voucher approval_level=3
        DB-->>ApprovalSvc: OK
        ApprovalSvc-->>Frontend: 200 OK
    else Level 2 Optional
        ApprovalSvc->>DB: UPDATE voucher approval_level=3
    end

    Manager->>Frontend: Final Approval (Level 3)
    Frontend->>ApprovalSvc: POST /approvals/{voucher_id}/approve?level=3
    ApprovalSvc->>DB: UPDATE voucher_approval SET status='A'
    ApprovalSvc->>DB: UPDATE voucher SET is_approved=true, is_locked=true
    DB-->>ApprovalSvc: OK
    ApprovalSvc-->>Frontend: 200 OK
    Note over VoucherSvc,DB: Voucher becomes immutable (except corrective voucher)
```

---

## Level 6 – Data Flow Diagram (DFD) – Level 0 & Level 1

### Level 0 – Context DFD

```mermaid
graph LR
    User[("User")] -->|Voucher Data, Queries| System[["Accounting System"]]
    System -->|Reports, Ledgers| User
    Tax[("Tax Authority")] <--|Export Files| System
    Bank[("Bank")] -->|CSV Import| System
    Audit[("Audit Log Store")] <--|Audit Events| System
```

### Level 1 – Major Processes

```mermaid
graph TD
    subgraph "Inputs"
        VoucherIn["Voucher Entry"]
        ImportIn["CSV Import"]
        ConfigIn["Config Changes"]
    end

    subgraph "Processes"
        P1["1.0 Validate & Record Voucher"]
        P2["2.0 Manage Chart of Accounts"]
        P3["3.0 Process Approvals"]
        P4["4.0 Generate Ledgers & Reports"]
        P5["5.0 Currency & Revaluation"]
        P6["6.0 Budget Monitoring"]
        P7["7.0 Audit Logging"]
        P8["8.0 Backup & Recovery"]
    end

    subgraph "Data Stores"
        D1[("Accounts DB")]
        D2[("Vouchers DB")]
        D3[("Ledgers DB")]
        D4[("Currencies DB")]
        D5[("Budgets DB")]
        D6[("Audit Log DB")]
        D7[("File Store")]
    end

    subgraph "Outputs"
        ReportOut["Financial Reports"]
        ExportOut["Tax Export Files"]
        AlertOut["Budget Alerts"]
        BackupOut["Backup Files"]
    end

    VoucherIn --> P1
    ImportIn --> P1
    ConfigIn --> P2
    P1 --> D2
    P1 --> D1
    P2 --> D1
    P3 --> D2
    P4 --> D3
    P4 --> ReportOut
    P5 --> D4
    P5 --> D2
    P6 --> D5
    P6 --> AlertOut
    P7 --> D6
    P8 --> D7
    P8 --> BackupOut
    D2 --> ExportOut
```

---

*All diagrams are expressed in Mermaid syntax for version-controlled, renderable documentation.*