# Unified Modeling Language (UML) - Entity Relationship Diagram (ERD)

This section provides the six-level relational database schema as an ERD, complementing the UML class diagrams and DFD from previous sections.

## Level 1: Database Context

```mermaid
entityDiagram
    "External Factors" --> "Accounting DB"
    "Accounting DB" --> "Users"
    "Tax Authority" --> "Accounting DB" (Export Files)
    "Bank" --> "Accounting DB" (CSV Import)
    "Audit System" <-"Accounting DB"

```

---

## Level 2: High-Level ERD

```mermaid
entityDiagram
    "Voucher Entities" --> "Chart of Accounts"
    "Chart of Accounts" --> "Budget Items"
    "Budget Items" --> "Journal Entries"
    "Journal Entries" <-> "Clients"
    "Journal Entries" --> "Exchange Rates"
    "Journal Entries" --> "Approval Workflows"
    "Journal Entries" --> "Audit Log"

    "Users" --> "Approval Workflows"
    "Users" --> "Budget Items"

```

---

## Level 3: Entity Types

```mermaid
entityDiagram
    "Chart of Accounts" {
        id: UUID, Primary Key
        code: VARCHAR(3)
        name_fa: VARCHAR(100)
        name_en: VARCHAR(100)
        parent_id: UUID (self-reference)
        level: INT (1-6)
        type: CHAR (T=Standard, D=Diff. Chart)
        is_active: BOOLEAN
    }

    "Journal Entries" {
        id: UUID, Primary Key
        voucher_no: VARCHAR(15)
        voucher_type: CHAR (N/C)
        period: VARCHAR(20)
        date: DATE
        debit: DECIMAL(18,4)
        credit: DECIMAL(18,4)
        account_id: UUID (FK to Chart of Accounts)
        counterparty_id: UUID (FK to Clients)
    }

    "Clients" {
        id: UUID
        name: VARCHAR(200)
        tax_id: VARCHAR(100)
        phone: VARCHAR(20)
        email: VARCHAR(100)
    }

    "Exchange Rates" {
        id: UUID
        currency_id: UUID (FK to Currencies)
        effective_date: DATE
        rate: DECIMAL(15,10)
    }

    "Currencies" {
        id: UUID
        code: VARCHAR(3)
        name_fa: VARCHAR(100)
        name_en: VARCHAR(100)
    }

    "Budgets" {
        id: UUID
        account_id: UUID (FK)
        period: VARCHAR(20)
        budget_amount: DECIMAL(18,4)
        actual_amount: DECIMAL(18,4)
        variance: DECIMAL(18,4)
    }

    "Approval Workflows" {
        id: UUID
        voucher_id: UUID (FK)
        level: INT (1-3)
        status: CHAR (A=Approved, N=Rejected, P=Pending)
        approved_by: UUID (FK to Users)
    }

    "Audit Log" {
        id: UUID
        user_id: UUID (FK)
        action: VARCHAR(50)
        entity_type: VARCHAR(30)
        entity_id: UUID
        timestamp: DATETIME
    }

```

---

## Level 4: Relationships Diagram

```mermaid
ec diagram
    "Chart of Accounts" --> "Journal Entries"
    "Journal Entries" -R-> "Clients"
    "Journal Entries" -R-> "Exchange Rates"
    "Journal Entries" --> "Approval Levels"
    "Approval Levels" --> "Approval Workflows"
    "Approval Workflows" -R-> "Journal Entries"
    "Chart of Accounts" --"0..*" "Budgets"
    "Budgets" --> "Audit Log"

```

---

## Level 5: Detailed Relationships

```mermaid
ec diagram
    "Account" "1" -> "0..*" "Journal Entry" : accounting_entry
    "Account" "1" -> "0..*" "Budget Item" : budget_tracking
    "Account" "1" -> "0..*" "Exchange Rate" : currency_link
    "Client" "1" -> "0..*" "Journal Entry" : counterparty
    "Approval Level" "1" -> "0..*" "Approval Workflow Step" : step_assignment
    "Approval Workflow Step" "1" -> "0..1" "User" : approver

```

---

## Level 6: Specialized Relationships

```mermaid
ec diagram
    "Voucher" "1" -[approves]-> "Approval Workflow Step" : level 1
    "Approval Workflow Step" "1" -[approves]-> "Approval Workflow Step" : level 2
    "Approval Workflow Step" "1" -[approves]-> "Approval Workflow Step" : level 3
    "Budget Item" "1" -[triggers]-> "Audit Alert" : overrun_detection
    "Audit Alert" "1" -[notifies]-> "User" : budget_overrun
    "Journal Entry" "1" -[locks]-> "Journal Entry" : immutable_state (when approved level 3)

```

---

*This ERD maps all core entities and their complex 6-level hierarchical relationships as specified in the requirements.*