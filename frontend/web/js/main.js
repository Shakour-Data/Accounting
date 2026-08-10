// Frontend JavaScript for Accounting System
const API_BASE = 'http://localhost:8000';

// Dashboard functions
async function loadDashboardStats() {
    try {
        const response = await fetch(API_BASE + '/dashboard/stats');
        const data = await response.json();
        document.getElementById('stats-container').innerHTML = `
            <div class="stat-card">
                <h3>Total Vouchers</h3>
                <p>${data.total_vouchers}</p>
            </div>
            <div class="stat-card">
                <h3>Accounts</h3>
                <p>${data.total_accounts}</p>
            </div>
            <div class="stat-card">
                <h3>Net Balance</h3>
                <p>${data.net_balance}</p>
            </div>
        `;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Account management functions
async function createAccount(accountData) {
    try {
        const response = await fetch(API_BASE + '/accounts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: accountData.code,
                name_fa: accountData.name_fa,
                name_en: accountData.name_en,
                level: accountData.level,
                account_type: accountData.type,
                normal_balance: accountData.normal_balance || 'D'
            })
        });
        const result = await response.json();
        loadAccounts();
        return result;
    } catch (error) {
        console.error('Error creating account:', error);
        throw error;
    }
}

async function loadAccounts() {
    try {
        const response = await fetch(API_BASE + '/accounts/');
        const accounts = await response.json();
        displayAccounts(accounts);
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

function displayAccounts(accounts) {
    const container = document.getElementById('accounts-container');
    container.innerHTML = accounts.map(acc => `
        <div class="account-item" style="margin-right: ${acc.level * 15}px">
            <span>[${acc.code}] ${acc.name_fa}</span>
            <button onclick="editAccount(${acc.id})">Edit</button>
        </div>
    `).join('');
}

// Journal entry functions
async function createJournalEntry(entry) {
    try {
        // Validate debit = credit
        const totalDebit = entry.rows.reduce((sum, r) => sum + parseFloat(r.debit || 0), 0);
        const totalCredit = entry.rows.reduce((sum, r) => sum + parseFloat(r.credit || 0), 0);
        
        if (Math.abs(totalDebit - totalCredit) > 0.01) {
            throw new Error('Total Debit (' + totalDebit + ') must equal Total Credit (' + totalCredit + ')');
        }

        const response = await fetch(API_BASE + '/vouchers/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                voucher_no: entry.voucher_no,
                voucher_type: entry.voucher_type || 'N',
                period: entry.period,
                voucher_date: entry.voucher_date,
                rows: entry.rows,
                description: entry.description,
                reference: entry.reference
            })
        });
        
        const result = await response.json();
        loadEntries();
        return result;
    } catch (error) {
        console.error('Error creating journal entry:', error);
        throw error;
    }
}

async function loadEntries() {
    try {
        const response = await fetch(API_BASE + '/vouchers/');
        const entries = await response.json();
        displayEntries(entries);
    } catch (error) {
        console.error('Error loading entries:', error);
    }
}

function displayEntries(entries) {
    const tbody = document.getElementById('entries-table-body');
    tbody.innerHTML = entries.map(entry => `
        <tr>
            <td>${entry.voucher_no}</td>
            <td>${new Date(entry.voucher_date).toLocaleDateString('fa-IR')}</td>
            <td>${entry.description_fa || ''}</td>
            <td>${entry.credit}</td>
            <td>${entry.debit}</td>
            <td>
                <span class="status-badge ${entry.is_approved ? 'status-active' : 'status-pending'}">
                    ${entry.is_approved ? 'Approved' : 'Pending'}
                </span>
            </td>
        </tr>
    `).join('');
}

// Approval workflow
async function approveVoucher(voucherId, level) {
    try {
        const response = await fetch(API_BASE + '/vouchers/' + voucherId + '/approve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ level })
        });
        const result = await response.json();
        loadEntries();
        return result;
    } catch (error) {
        console.error('Error approving voucher:', error);
        throw error;
    }
}

// Financial reports
async function loadBalanceSheet() {
    try {
        const response = await fetch(API_BASE + '/financial-statement/balance-sheet');
        const data = await response.json();
        
        const assetsHtml = data.assets.map(a => `
            <tr><td>${a.name}</td><td dir="ltr">${a.balance}</td></tr>
        `).join('');
        
        const content = `
            <h3>Balance Sheet</h3>
            <table class="table">
                <tr><th colspan="2">Assets</th></tr>
                ${assetsHtml}
                <tr><td><strong>Total Assets</strong></td><td dir="ltr"><strong>${data.asset_total}</strong></td></tr>
            </table>
        `;
        document.getElementById('report-content').innerHTML = content;
    } catch (error) {
        console.error('Error loading balance sheet:', error);
    }
}

async function loadProfitLoss() {
    try {
        const response = await fetch(API_BASE + '/financial-statement/profit-loss');
        const data = await response.json();
        
        const content = `
            <h3>Profit & Loss</h3>
            <table class="table">
                <tr><th>Revenues</th><th></th></tr>
                ${data.revenues.map(r => `
                    <tr><td>${r.name}</td><td dir="ltr">${r.balance}</td></tr>
                `).join('')}
                <tr><th>Expenses</th><th></th></tr>
                ${data.expenses.map(e => `
                    <tr><td>${e.name}</td><td dir="ltr">${e.balance}</td></tr>
                `).join('')}
                <tr><td><strong>Net ${data.profit_or_loss}</strong></td><td dir="ltr"><strong>${data.net_profit}</strong></td></tr>
            </table>
        `;
        document.getElementById('report-content').innerHTML = content;
    } catch (error) {
        console.error('Error loading P&L:', error);
    }
}

// Navigation
function showSection(sectionName) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('section').forEach(section => {
        section.style.display = 'none';
    });
    
    document.getElementById(sectionName + '-section').classList.add('active');
    document.getElementById(sectionName + '-section').style.display = 'block';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadAccounts();
    loadEntries();
});