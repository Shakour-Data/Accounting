# Request for Design and Development of an Advanced Accounting System  
## Fully Localized for Iran – 6-Level Chart of Accounts

---

### 1. Project Overview
The goal is to design and develop a fully integrated accounting system with professional-grade capabilities, suitable for both Small and Medium Enterprises (SMEs) and personal financial management. The system must be entirely in Persian, use the Solar Hijri calendar, and fully comply with Iranian Accounting Standards. All advanced features—including fiscal periods, a 6-level chart of accounts, approval workflows, multi-currency management, and analytical reporting—must be included.

---

### 2. Core System Features

**A) Fiscal Period Management**  
Define flexible fiscal periods (monthly, quarterly, yearly) with independent opening/closing. The system must block entries in closed periods and allow corrections only with manager-level authorization.

**B) Chart of Accounts (6-Level Coding)**  
Support a hierarchical structure with up to **6 levels** (Main Group, Sub-Group, General Ledger, Subsidiary, Detail 1, Detail 2). The coding must follow the Iranian accounting framework (9 main groups) with full user customization. Off-balance-sheet, contingent, and memorandum accounts must also be definable within this structure.

**C) Journal Entry Recording**  
Each voucher must include:
- Auto-numbering (separate for normal, corrective, and closing entries)
- Voucher templates for recurring transactions
- Multiple rows with description, amount, counterparty, and selection from any of the 6 coding levels per row
- File attachment (receipts, invoices, contracts) per voucher
- Automatic validation of the accounting equation (Debit = Credit)

**D) Approval Workflow**  
Support at least **3 approval levels**:
- Level 1: Entry (Draft)
- Level 2: Accountant Approval
- Level 3: Final Manager Approval  
Each level must be configurable as mandatory or optional per voucher type.

**E) Legal and Analytical Ledgers**  
Automatically generate the following ledgers with filtering by period, date, and any coding level:
- Journal (with Solar Hijri date and voucher number)
- General Ledger (balances at each level)
- Subsidiary Ledger (customer/supplier/bank details)
- Detail Ledger (down to all 6 levels, e.g., project/branch/department costs)  
All ledgers must be exportable to PDF and Excel.

**F) Multi-Currency Management**  
Define multiple currencies (USD, EUR, AED) with real-time and average exchange rates. The system must record foreign-currency vouchers with automatic Rial conversion and generate year-end revaluation entries.

**G) Advanced Financial Statements**  
- Comparative Balance Sheet (current vs. prior period)  
- Profit & Loss by month with percentage variance  
- Cash Flow Statement (direct and indirect methods)  
- Aging reports for receivables/payables (current, overdue, doubtful)

**H) Invoicing and Billing**  
Issue sales/purchase invoices with automatic VAT calculation, discounts/surcharges, linkage to subsidiary/detail accounts, and generate standard files for submission to the Iranian tax authority (Saman-e Moo'adian).

**I) Budgeting and Control**  
Define budgets for any account at any of the 6 levels per period, display variance (actual vs. budget), and issue alerts for budget overruns.

**J) Analytical Reports**  
- Account balance reports by each coding level  
- Subsidiary/Detail reports with multiple filters (date, amount, counterparty, coding level)  
- P&L and income/expense charts (line and bar)  
- Closing temporary accounts (closing entries) at period-end

---

### 3. Personal Mode (alongside Professional Mode)
The system must have **two modes** within a single environment:
- **Professional Mode:** All above features with 6-level coding (for businesses)
- **Simple Mode:** Only income/expense recording, balance view, and personal budgeting (no double-entry, no periods, no approval levels) – with seamless switching between modes at any time.

---

### 4. Technical and Localization Requirements
- **Language & Calendar:** Entire UI in Persian, primary calendar = Solar Hijri, Persian numerals, Persian font (Vazirmatn)  
- **Backup:** Automated daily backups + Point-in-Time recovery  
- **Security:** AES-256 encryption, full audit log (user, timestamp, changed voucher)  
- **Accessibility:** Web-based, responsive on desktop and mobile browsers  
- **Exports:** PDF, Excel, CSV with fully Persian/RTL formatting

---

### 5. Out of Scope (Phase 1)
- Full payroll module (only simple salary payment recording is allowed)  
- Inventory and stock management  
- Direct bank gateway integration (only CSV import supported)  
- Production and cost accounting module

---

### 6. Deliverables
1. System architecture, data model, and 6-level coding structure documentation  
2. Beta version with voucher entry, GL, and subsidiary ledgers  
3. Final version with all reports, fiscal periods, and 6-level coding  
4. Complete Persian user manual + short training video

---

### 7. Acceptance Criteria
- All calculations must comply with Iranian Accounting Standards (Nos. 168 & 169 of the Audit Organization).  
- Journal, GL, subsidiary, and detail ledgers at all 6 levels must generate without errors.  
- Any voucher approved at Level 3 must become immutable (except via corrective voucher).  
- Report loading time with 10,000 vouchers must be under 5 seconds.  
- Tax authority export files must be accepted by the Iranian tax system.

---

### Conclusion
The development team must deliver the system with maximum accuracy, security, and professional completeness within a **6-month timeframe**. Monthly review meetings are mandatory.