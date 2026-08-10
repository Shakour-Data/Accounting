import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "accounting.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    name_fa = Column(String(100), nullable=False)
    name_en = Column(String(100))
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    level = Column(Integer, nullable=False)
    account_type = Column(String(1))  # T=تراز موجودیها, D=معادل‌ها, H=حساب‌های دوره‌ای
    is_active = Column(Boolean, default=True)
    normal_balance = Column(String(1), default="D")  # D=طلب, C=علیه
    created_at = Column(DateTime, default=datetime.utcnow)
    
    parent = relationship("Account", back_populates="children", remote_side=[id])
    children = relationship("Account", back_populates="parent")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True)
    voucher_no = Column(String(30), unique=True, nullable=False)
    voucher_type = Column(String(1), nullable=False)  # N=عادی, C=تصحیح, K=بستنی
    period = Column(String(20), nullable=False)
    voucher_date = Column(DateTime, default=datetime.utcnow)
    debit = Column(DECIMAL(18, 4), default=0)
    credit = Column(DECIMAL(18, 4), default=0)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    description_fa = Column(Text)
    is_approved = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    approval_level = Column(Integer, default=0)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VoucherRow(Base):
    __tablename__ = "voucher_rows"
    
    id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit = Column(DECIMAL(18, 4), default=0)
    credit = Column(DECIMAL(18, 4), default=0)
    description = Column(Text)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    tax_id = Column(String(50))
    type = Column(String(1))  # C=مشتری, P=تأمین‌کننده, B=بانک

class Currency(Base):
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)
    name_fa = Column(String(50), nullable=False)
    rate = Column(DECIMAL(15, 6), default=1.0)
    is_active = Column(Boolean, default=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()