from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.invoice_portal import InvoiceDocument

class InvoiceService:
    @staticmethod
    def search_invoices(db: Session, company: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        q = db.query(InvoiceDocument)
        if company:
            q = q.filter(InvoiceDocument.company.ilike(f"%{company}%"))
        if query:
            q = q.filter(
                (InvoiceDocument.invoice_number.ilike(f"%{query}%")) |
                (InvoiceDocument.raw_content.ilike(f"%{query}%"))
            )
        # Order by issue_date descending so the latest is clearly visible
        invoices = q.order_by(desc(InvoiceDocument.issue_date)).all()
        return [inv.to_dict() for inv in invoices]

    @staticmethod
    def get_invoice(db: Session, invoice_number: str) -> Optional[Dict[str, Any]]:
        inv = db.query(InvoiceDocument).filter(
            InvoiceDocument.invoice_number.ilike(invoice_number.strip())
        ).first()
        return inv.to_dict() if inv else None

    @staticmethod
    def list_all(db: Session) -> List[Dict[str, Any]]:
        invoices = db.query(InvoiceDocument).order_by(desc(InvoiceDocument.issue_date)).all()
        return [inv.to_dict() for inv in invoices]
