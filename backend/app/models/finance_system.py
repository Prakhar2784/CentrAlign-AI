from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class FinanceInvoiceRecord(Base):
    __tablename__ = "finance_invoice_records"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    company = Column(String(100), index=True, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    due_date = Column(String(20), nullable=True)
    currency = Column(String(10), default="USD")
    sync_status = Column(String(30), default="PENDING_REVIEW")
    last_verified_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "company": self.company,
            "amount": self.amount,
            "due_date": self.due_date,
            "currency": self.currency,
            "sync_status": self.sync_status,
            "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
