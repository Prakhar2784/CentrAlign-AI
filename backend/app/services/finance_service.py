from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.finance_system import FinanceInvoiceRecord
from app.core.logging import logger

def utcnow():
    return datetime.now(timezone.utc)

class FinanceService:
    @staticmethod
    def search_records(db: Session, company: Optional[str] = None, invoice_number: Optional[str] = None) -> List[Dict[str, Any]]:
        q = db.query(FinanceInvoiceRecord)
        if company:
            q = q.filter(FinanceInvoiceRecord.company.ilike(f"%{company}%"))
        if invoice_number:
            q = q.filter(FinanceInvoiceRecord.invoice_number.ilike(f"%{invoice_number.strip()}%"))
        records = q.all()
        return [rec.to_dict() for rec in records]

    @staticmethod
    def get_record(db: Session, invoice_number: str) -> Optional[Dict[str, Any]]:
        rec = db.query(FinanceInvoiceRecord).filter(
            FinanceInvoiceRecord.invoice_number.ilike(invoice_number.strip())
        ).first()
        return rec.to_dict() if rec else None

    @staticmethod
    def list_all(db: Session) -> List[Dict[str, Any]]:
        records = db.query(FinanceInvoiceRecord).order_by(FinanceInvoiceRecord.id).all()
        return [rec.to_dict() for rec in records]

    @staticmethod
    def update_invoice_record(
        db: Session,
        invoice_number: str,
        amount: float,
        due_date: str,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        simulate_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Updates an invoice record in the finance ledger.
        If simulate_failure is True, simulates a transient 503 lock exception.
        """
        if simulate_failure:
            logger.warning(f"Simulating transient failure for finance update of {invoice_number}")
            return {
                "success": False,
                "error": "FINANCE_DB_LOCK_TIMEOUT: Ledger lock collision on financial periods table. Retry recommended.",
                "retryable": True,
                "invoice_number": invoice_number
            }

        rec = db.query(FinanceInvoiceRecord).filter(
            FinanceInvoiceRecord.invoice_number.ilike(invoice_number.strip())
        ).first()

        if not rec:
            # Create record if not pre-existing
            rec = FinanceInvoiceRecord(
                invoice_number=invoice_number.strip(),
                company=company or "Unknown",
                amount=float(amount),
                due_date=due_date.strip(),
                sync_status="SYNCED",
                notes=notes or "Auto-synced by Autonomous Task Worker"
            )
            db.add(rec)
        else:
            rec.amount = float(amount)
            rec.due_date = due_date.strip()
            if company:
                rec.company = company
            rec.sync_status = "SYNCED"
            rec.notes = notes or f"Updated autonomously at {utcnow().isoformat()}"

        db.commit()
        db.refresh(rec)
        logger.info(f"Successfully updated finance record for {invoice_number}: amount={amount}, due_date={due_date}")
        return {
            "success": True,
            "record": rec.to_dict(),
            "message": f"Invoice record {invoice_number} successfully updated in finance database."
        }

    @staticmethod
    def verify_invoice_record(
        db: Session,
        invoice_number: str,
        expected_amount: float,
        expected_due_date: str,
        expected_company: Optional[str] = None,
        simulate_verification_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Independently reads back the record from the database and checks for discrepancy.
        """
        rec = db.query(FinanceInvoiceRecord).filter(
            FinanceInvoiceRecord.invoice_number.ilike(invoice_number.strip())
        ).first()

        if not rec:
            return {
                "verified": False,
                "reason": f"Record {invoice_number} does not exist in the finance ledger.",
                "invoice_number": invoice_number
            }

        if simulate_verification_failure:
            return {
                "verified": False,
                "reason": "SIMULATED_CHECKSUM_DISCREPANCY: Financial auditor checksum failed. Record verification rejected.",
                "stored_values": rec.to_dict(),
                "expected_values": {
                    "amount": expected_amount,
                    "due_date": expected_due_date,
                    "company": expected_company
                }
            }

        discrepancies = []
        if abs(float(rec.amount) - float(expected_amount)) > 0.01:
            discrepancies.append(f"Amount mismatch: expected {expected_amount}, found {rec.amount}")
        if rec.due_date != expected_due_date:
            discrepancies.append(f"Due date mismatch: expected {expected_due_date}, found {rec.due_date}")
        if expected_company and expected_company.lower() not in rec.company.lower():
            discrepancies.append(f"Company mismatch: expected {expected_company}, found {rec.company}")

        if discrepancies:
            return {
                "verified": False,
                "reason": "Discrepancy detected during independent read-back verification.",
                "discrepancies": discrepancies,
                "stored_values": rec.to_dict()
            }

        rec.last_verified_at = utcnow()
        db.commit()

        return {
            "verified": True,
            "message": f"Verification PASSED for invoice {invoice_number}. Stored database record matches expected values.",
            "verified_record": rec.to_dict()
        }
