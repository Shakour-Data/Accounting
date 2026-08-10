from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AccountBase(BaseModel):
    code: str
    name_fa: str
    name_en: Optional[str] = None
    level: int
    account_type: str
    is_active: bool = True
    normal_balance: str = "D"

class AccountCreate(AccountBase):
    parent_id: Optional[int] = None

class AccountResponse(AccountBase):
    id: int
    parent_id: Optional[int] = None
    children: List["AccountResponse"] = []
    
    class Config:
        from_attributes = True

AccountResponse.update_forward_refs()

class JournalEntryBase(BaseModel):
    voucher_no: str
    voucher_type: str
    period: str
    voucher_date: datetime
    debit: float
    credit: float
    account_id: int
    description_fa: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntryResponse(JournalEntryBase):
    id: int
    is_approved: bool
    is_locked: bool
    approval_level: int
    
    class Config:
        from_attributes = True

class VoucherRowCreate(BaseModel):
    account_id: int
    debit: float = 0
    credit: float = 0
    description: Optional[str] = None

class VoucherCreate(BaseModel):
    voucher_no: str
    voucher_type: str = "N"
    period: str
    voucher_date: datetime
    rows: List[VoucherRowCreate]
    description: Optional[str] = None

class ApproveRequest(BaseModel):
    voucher_id: int
    level: int