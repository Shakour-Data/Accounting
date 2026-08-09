# BPMN Workflows

Business Process Model & Notation diagrams for the core Accounting System workflows.

---

## Workflow 1 – Voucher Lifecycle & Approval

```mermaid
bpmn
    participant "Accountant" as Accountant
    participant "Approval System" as ApprovalSystem
    participant "Audit Log" as AuditLog

    Accountant -> Accountant: Start (Voucher Entry)
    Accountant -> ApprovalSystem: Create Voucher (Draft, Level 0)
    ApprovalSystem -> AuditLog: Log Create Event
    Accountant -> ApprovalSystem: Submit for Approval (Level 1)
    ApprovalSystem -> ApprovalSystem: Validate Debit=Credit
    ApprovalSystem -> AuditLog: Log Submit Event
    ApprovalSystem -> Accountant: Pending Approval L1
    alt Level 1 Mandatory
        Accountant -> ApprovalSystem: Approve Level 1
        ApprovalSystem -> AuditLog: Log Approval L1
        ApprovalSystem -> Accountant: Pending Approval L2
    end
    alt Level 2 Mandatory
        Accountant -> ApprovalSystem: Approve Level 2
        ApprovalSystem -> AuditLog: Log Approval L2
    end
    Accountant -> ApprovalSystem: Final Approval (Level 3)
    ApprovalSystem -> AuditLog: Log Approval L3
    ApprovalSystem -> ApprovalSystem: Lock Voucher (Immutable)
    ApprovalSystem -> Accountant: Voucher Approved & Locked
    Accountant -> Accountant: End
```

---

## Workflow 2 – Month-End Closing

```mermaid
bpmn
    participant "Manager" as Manager
    participant "Closing Engine" as ClosingEngine
    participant "General Ledger" as GeneralLedger
    participant "Audit Log" as AuditLog

    Manager -> Manager: Trigger Month-End Close
    Manager -> ClosingEngine: Close Period
    ClosingEngine -> GeneralLedger: Snapshot Balances
    ClosingEngine -> ClosingEngine: Generate Closing Entries
    ClosingEngine -> AuditLog: Log Closing Event
    ClosingEngine -> Manager: Period Closed
    Manager -> Manager: End
```

---

## Workflow 3 – Budget Overrun Alert

```mermaid
bpmn
    bpmnSubProcess "Monitor Budget"
        bpmnTask "Compare Actual vs Budget"
        bpmnGateway "Overrun?"
        bpmnTask "Issue Alert"
    end

    StartEvent("Daily Budget Check") -> MonitorBudget
    MonitorBudget -> EndEvent("Alert or OK")
```
