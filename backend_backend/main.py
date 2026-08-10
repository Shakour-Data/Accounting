import os
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import QueuePool

# --- Configuration ---
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "accounting.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-secret-change-in-production")

# --- Database Engine & Session ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), nullable=False)
    name_fa = Column(String(100), nullable=False)
    name_en = Column(String(100))
    parent_id = Column(Integer, ForeignKey("accounts.id"))
    level = Column(Integer, nullable=False)  # 1-6
    account_type = Column(String(1), nullable=False)  # T=تراز, م=معادل, ح=حساب
    normal_balance = Column(String(1), default="D")  # D=طلب, C=علیه
    is_active = Column(Boolean, default=True)
    is_memo = Column(Boolean, default=False)
    is_contingent = Column(Boolean, default=False)
    currency_code = Column(String(3), default="IRR")
    description = Column(Text)
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    children = relationship("Account", backref=relationship("parent", remote_side=[id]))


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    voucher_no = Column(String(15), nullable=False, unique=True)
    voucher_type = Column(String(1), nullable=False)  # N=عادی, C=تصحیح, K=بستنی
    period = Column(String(20), nullable=False)
    voucher_date = Column(DateTime, nullable=False)
    debit = Column(DECIMAL(18, 4))
    credit = Column(DECIMAL(18, 4))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    account_code = Column(String(10))
    account_name = Column(String(100))
    counterparty = Column(String(100))
    description_fa = Column(Text)
    description_en = Column(Text)
    reference = Column(String(50))
    approval_level = Column(Integer, default=0)  # 0=پیش‌نویس, 1=حسابدار, 2=مدیر
    is_approved = Column(Boolean, default=False)
    is_correction = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_system_generated = Column(Boolean, default=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VoucherRow(Base):
    __tablename__ = "voucher_rows"

    id = Column(Integer, primary_key=True, index=True)
    voucher_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit = Column(DECIMAL(18, 4))
    credit = Column(DECIMAL(18, 4))
    description = Column(Text)
    counterparty = Column(String(100))


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_fa = Column(String(100))
    client_type = Column(String(1), nullable=False)  # C=مشتری, P=تامین‌کننده, B=بانک
    tax_id = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), nullable=False, unique=True)
    name_fa = Column(String(50), nullable=False)
    name_en = Column(String(50))
    symbol = Column(String(5))
    is_active = Column(Boolean, default=True)


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency_code = Column(String(3), ForeignKey("currencies.code"))
    rate = Column(DECIMAL(15, 6), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    rate_type = Column(String(1))  # R=رسمی, E=متوسط, A=خرید, S=فروش
    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    period = Column(String(20), nullable=False)
    budget_amount = Column(Decimal(18, 4))
    actual_amount = Column(Decimal(18, 4))
    variance = Column(Decimal(18, 4))
    is_active = Column(Boolean, default=True)


class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_open = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(30), nullable=False)
    entity_id = Column(Integer)
    entity_name = Column(String(100))
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="USER")  # ADMIN, ACCOUNTANT, MANAGER, USER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


# --- Database Setup ---
def init_db():
    Base.metadata.create_all(bind=engine)
    seed_data()


def seed_data():
    db = SessionLocal()
    # Seed currencies
    if not db.query(Currency).first():
        db.add_all([
            Currency(code="IRR", name_fa="ریال", name_en="Iranian Rial", symbol="﷼", is_active=True),
            Currency(code="USD", name_fa="دلار", name_en="US Dollar", symbol="$", is_active=True),
            Currency(code="EUR", name_fa="یورو", name_en="Euro", symbol="€", is_active=True),
            Currency(code="AED", name_fa="درهم", name_en="UAE Dirham", symbol="د.إ", is_active=True),
        ])
    # Seed default admin user
    if not db.query(User).first():
        db.add(User(
            username="admin",
            email="admin@accounting.local",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA/7.J6L1yq",
            full_name="Administrator",
            role="ADMIN"
        ))
    # Seed 9 main account groups (Iranian standard)
    if not db.query(Account).first():
        main_groups = [
            ("100", "دارایی ها", "Assets", 1),
            ("200", "بدهی ها", "Liabilities", 2),
            ("300", "سرمایه", "Equity", 3),
            ("400", "درآمدها", "Revenues", 4),
            ("500", "هزینه ها", "Expenses", 5),
            ("600", "هزینه مالی", "Financial Expenses", 6),
            ("700", "سایر", "Other", 7),
            ("800", "حساب‌های موقت", "Temporary Accounts", 8),
            ("900", "حساب‌های تکمیلی", "Supplementary Accounts", 9),
        ]
        db.add_all([
            Account(
                code=code, name_fa=name_fa, name_en=name_en,
                level=1, account_type="م", normal_balance="D"
            )
            for code, name_fa, name_en, level in main_groups
        ])
    # Seed financial period
    if not db.query(FinancialPeriod).first():
        db.add(FinancialPeriod(
            name="1403-1404",
            start_date=datetime(2024, 3, 20),
            end_date=datetime(2025, 3, 20),
            is_open=True,
            is_locked=False
        ))
    db.commit()
    db.close()


# --- FastAPI Application ---
app = FastAPI(
    title="Accounting System API",
    description="Multi-platform Accounting System for Iranian SMEs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Pydantic Models ---
class VoucherRowCreate(BaseModel):
    account_id: int
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    counterparty: Optional[str] = None


class VoucherCreate(BaseModel):
    voucher_no: str
    voucher_type: str = "N"
    period: str
    voucher_date: datetime
    rows: List[VoucherRowCreate]
    description: Optional[str] = None
    reference: Optional[str] = None


class VoucherResponse(BaseModel):
    id: int
    voucher_no: str
    voucher_type: str
    period: str
    voucher_date: datetime
    debit: float
    credit: float
    approval_level: int
    is_approved: bool
    is_correction: bool
    is_locked: bool
    rows: List[VoucherRowCreate] = []
    created_at: datetime
    modified_at: datetime
    account_name: Optional[str] = None
    account_code: Optional[str] = None
    counterparty: Optional[str] = None
    description_fa: Optional[str] = None

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id: int
    code: str
    name_fa: str
    name_en: Optional[str]
    level: int
    account_type: str
    is_active: bool
    children: List["AccountResponse"] = []

    class Config:
        from_attributes = True


AccountResponse.update_forward_refs()


# --- Routes ---
@app.get("/")
async def root():
    return {"message": "Accounting System API v1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/dashboard/stats")
async def dashboard_stats(db: SessionLocal = Depends(get_db)):
    total_vouchers = db.query(JournalEntry).count()
    total_accounts = db.query(Account).count()
    total_debit = db.query(JournalEntry).with_entities(
        JournalEntry.debit).with_entities(
        JournalEntry.debit).all()
    total_credit = db.query(JournalEntry).all()
    total_assets = total_debit - total_credit if total_debit else 0
    recent_vouchers = db.query(JournalEntry).order_by(
        JournalEntry.created_at.desc()).limit(5).all()
    return {
        "total_vouchers": total_vouchers,
        "total_accounts": total_accounts,
        "net_balance": str(total_assets),
        "recent_vouchers": [v.voucher_no for v in recent_vouchers]
    }


@app.post("/vouchers/", response_model=VoucherResponse)
async def create_voucher(voucher: VoucherCreate, db: SessionLocal = Depends(get_db)):
    total_debit = sum(r.debit for r in voucher.rows)
    total_credit = sum(r.credit for r in voucher.rows)

    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Debit ({total_debit}) must equal Credit ({total_credit})"
        )

    main_entry = JournalEntry(
        voucher_no=voucher.voucher_no,
        voucher_type=voucher.voucher_type,
        period=voucher.period,
        voucher_date=voucher.voucher_date,
        debit=Decimal(str(total_debit)),
        credit=Decimal(str(total_credit)),
        description_fa=voucher.description,
        reference=voucher.reference,
        approval_level=0,
        is_approved=False
    )
    db.add(main_entry)
    db.flush()

    for row in voucher.rows:
        db_row = VoucherRow(
            voucher_id=main_entry.id,
            account_id=row.account_id,
            debit=Decimal(str(row.debit)),
            credit=Decimal(str(row.credit)),
            description=row.description,
            counterparty=row.counterparty
        )
        db.add(db_row)

    audit = AuditLog(
        action="INSERT",
        entity_type="JournalEntry",
        entity_id=main_entry.id,
        entity_name=f"Voucher-{main_entry.voucher_no}",
        new_value=str(total_debit)
    )
    db.add(audit)
    db.commit()
    db.refresh(main_entry)

    return {
        "id": main_entry.id,
        "voucher_no": main_entry.voucher_no,
        "voucher_type": main_entry.voucher_type,
        "period": main_entry.period,
        "voucher_date": main_entry.voucher_date,
        "debit": float(main_entry.debit),
        "credit": float(main_entry.credit),
        "approval_level": main_entry.approval_level,
        "is_approved": main_entry.is_approved,
        "is_correction": main_entry.is_correction,
        "is_locked": main_entry.is_locked,
        "rows": voucher.rows,
        "created_at": main_entry.created_at,
        "modified_at": main_entry.modified_at
    }


@app.get("/vouchers/", response_model=List[VoucherResponse])
async def list_vouchers(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    vouchers = db.query(JournalEntry).offset(skip).limit(limit).all()
    result = []
    for v in vouchers:
        rows = db.query(VoucherRow).filter(VoucherRow.voucher_id == v.id).all()
        row_list = []
        for r in rows:
            account = db.query(Account).get(r.account_id)
            row_list.append(VoucherRowCreate(
                account_id=r.account_id,
                debit=float(r.debit),
                credit=float(r.credit),
                description=r.description,
                counterparty=r.counterparty
            ))
        result.append({
            "id": v.id,
            "voucher_no": v.voucher_no,
            "voucher_type": v.voucher_type,
            "period": v.period,
            "voucher_date": v.voucher_date,
            "debit": float(v.debit) if v.debit else 0,
            "credit": float(v.credit) if v.credit else 0,
            "approval_level": v.approval_level,
            "is_approved": v.is_approved,
            "is_correction": v.is_correction,
            "is_locked": v.is_locked,
            "rows": row_list,
            "created_at": v.created_at,
            "modified_at": v.modified_at,
            "account_name": v.account_name,
            "account_code": v.account_code,
            "counterparty": v.counterparty,
            "description_fa": v.description_fa
        })
    return result


@app.get("/accounts/", response_model=List[AccountResponse])
async def list_accounts(db: SessionLocal = Depends(get_db)):
    accounts = db.query(Account).order_by(Account.code).all()
    def build_account_tree(accs, parent_id=None):
        result = []
        for a in accs:
            if a.parent_id == parent_id:
                children = build_account_tree(accs, a.id)
                result.append(AccountResponse(
                    id=a.id,
                    code=a.code,
                    name_fa=a.name_fa,
                    name_en=a.name_en,
                    level=a.level,
                    account_type=a.account_type,
                    is_active=a.is_active,
                    children=children
                ))
        return result
    return build_account_tree(accounts)


@app.get("/accounts/{account_id}/ledger")
async def account_ledger(account_id: int, db: SessionLocal = Depends(get_db)):
    entries = db.query(JournalEntry).filter(JournalEntry.account_id == account_id).all()
    rows = db.query(VoucherRow).filter(VoucherRow.account_id == account_id).all()
    total_debit = sum(float(r.debit) for r in rows if r.debit)
    total_credit = sum(float(r.credit) for r in rows if r.credit)
    balance = total_debit - total_credit
    account = db.query(Account).get(account_id)
    return {
        "account": {"id": account.id, "code": account.code, "name_fa": account.name_fa},
        "transactions": [{"id": e.id, "voucher_no": e.voucher_no, "date": e.voucher_date,
                          "debit": float(e.debit) if e.debit else 0,
                          "credit": float(e.credit) if e.credit else 0,
                          "description": e.description_fa} for e in entries],
        "total_debit": str(total_debit),
        "total_credit": str(total_credit),
        "balance": str(balance),
        "balance_type": "طلب" if balance >= 0 else "علیه"
    }


@app.post("/vouchers/{voucher_id}/approve")
async def approve_voucher(voucher_id: int, level: int, db: SessionLocal = Depends(get_db)):
    voucher = db.query(JournalEntry).get(voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    if voucher.is_locked:
        raise HTTPException(status_code=400, detail="Voucher is immutable")
    if level > voucher.approval_level:
        voucher.approval_level = level
    if level >= 3:
        voucher.is_approved = True
        voucher.is_locked = True
    db.add(voucher)
    audit = AuditLog(
        action="APPROVE",
        entity_type="JournalEntry",
        entity_id=voucher_id,
        entity_name=voucher.voucher_no,
        new_value=f"Level {level}"
    )
    db.add(audit)
    db.commit()
    return {"status": "approved", "level": level, "locked": voucher.is_locked}


@app.post("/vouchers/{voucher_id}/correct")
async def create_correction(voucher_id: int, correction: VoucherCreate, db: SessionLocal = Depends(get_db)):
    original = db.query(JournalEntry).get(voucher_id)
    if not original or not original.is_locked:
        raise HTTPException(status_code=400, detail="Original must be approved and locked")
    correction.voucher_type = "C"
    correction.voucher_date = datetime.utcnow()
    response = await create_voucher(correction, db)
    audit = AuditLog(
        action="CORRECT",
        entity_type="JournalEntry",
        entity_id=original.id,
        entity_name=f"Correction-{response.id}"
    )
    db.add(audit)
    db.commit()
    return response


@app.get("/financial-statement/balance-sheet")
async def balance_sheet(db: SessionLocal = Depends(get_db)):
    assets = db.query(Account).filter(Account.level == 1, Account.code.like("1%%")).all()
    liabilities = db.query(Account).filter(Account.level == 1, Account.code.like("2%%")).all()
    equity = db.query(Account).filter(Account.level == 1, Account.code.like("3%%")).all()
    accounts_list = db.query(Account).all()

    def get_account_balance(acc_id):
        rows = db.query(VoucherRow).filter(VoucherRow.account_id == acc_id).all()
        d = sum(float(r.debit) for r in rows if r.debit)
        c = sum(float(r.credit) for r in rows if r.credit)
        account = db.query(Account).get(acc_id)
        normal = "D" if account.normal_balance == "D" else "C"
        balance = d - c if normal == "D" else c - d
        return balance

    asset_total = sum(get_account_balance(a.id) for a in assets)
    liability_total = sum(get_account_balance(a.id) for a in liabilities)
    equity_total = sum(get_account_balance(a.id) for a in equity)
    return {
        "assets": [{"name": a.name_fa, "balance": str(get_account_balance(a.id))} for a in assets],
        "liabilities": [{"name": l.name_fa, "balance": str(get_account_balance(l.id))} for l in liabilities],
        "equity": [{"name": e.name_fa, "balance": str(get_account_balance(e.id))} for e in equity],
        "asset_total": str(asset_total),
        "liability_total": str(liability_total),
        "equity_total": str(equity_total)
    }


@app.get("/financial-statement/profit-loss")
async def profit_loss(period: str = "all", db: SessionLocal = Depends(get_db)):
    revenues = db.query(Account).filter(Account.code.like("4%%")).all()
    expenses = db.query(Account).filter(Account.code.like("5%%")).all()
    def get_account_balance(acc_id):
        rows = db.query(VoucherRow).filter(VoucherRow.account_id == acc_id).all()
        d = sum(float(r.debit) for r in rows if r.debit)
        c = sum(float(r.credit) for r in rows if r.credit)
        return d - c
    revenue_total = sum(get_account_balance(a.id) for a in revenues)
    expense_total = sum(get_account_balance(a.id) for a in expenses)
    net_profit = revenue_total - expense_total
    return {
        "revenues": [{"name": a.name_fa, "balance": str(get_account_balance(a.id))} for a in revenues],
        "expenses": [{"name": e.name_fa, "balance": str(get_account_balance(e.id))} for e in expenses],
        "net_profit": str(abs(net_profit)),
        "profit_or_loss": "سود" if net_profit >= 0 else "زیان"
    }


init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
