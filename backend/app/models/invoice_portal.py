from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class InvoiceDocument(Base):
    __tablename__ = "portal_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    company = Column(String(100), index=True, nullable=False)
    issue_date = Column(String(20), nullable=False)
    due_date = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(30), default="ISSUED")
    raw_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "company": self.company,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "raw_content": self.raw_content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
