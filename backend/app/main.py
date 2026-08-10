# Accounting System Backend
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import uvicorn

# Database Configuration
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "accounting.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
SESSION_LOCAL = SessionLocal()

# Base Models
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    name_fa = Column(String(100), nullable=False)
    name_en = Column(String(100))
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    level = Column(Integer, nullable=False)
    account_type = Column(String(1))
    is_active = Column(Boolean, default=True)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    voucher_no = Column(String(30), unique=True, nullable=False)
    voucher_type = Column(String(1), nullable=False)
    period = Column(String(20), nullable=False)
    voucher_date = Column(DateTime, default=datetime.utcnow)
    debit = Column(Decimal(18, 4), default=0)
    credit = Column(Decimal(18, 4), default=0)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    description_fa = Column(Text)


# Initialize Database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI App
app = FastAPI(
    title="Accounting System API",
    description="Multiplatform Finance Management System",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Versioning
class StatusResponse(BaseModel):
    status: str = "success"
    message: str = ""

# Root endpoint
@app.get("/", response_model=StatusResponse)
async def root():
    return StatusResponse(status="ok", message="Accounting System API v1")

# Health check endpoint
@app.get("/health", response_model=StatusResponse)
async def health():
    return StatusResponse(status="ok", message="Service operational")

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)