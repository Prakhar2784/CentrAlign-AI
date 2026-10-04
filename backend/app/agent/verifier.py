from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.services.finance_service import FinanceService
from app.core.logging import logger

class TaskVerifier:
    """
    Independent Verification Engine:
    Validates that database state reflects exact expectations before task completion is acknowledged.
    """
    
    @staticmethod
    def verify_persisted_state(
        db: Session,
        extracted_data: Dict[str, Any],
        simulate_verification_failure: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        invoice_number = extracted_data.get("invoice_number")
        expected_amount = extracted_data.get("amount")
        expected_due_date = extracted_data.get("due_date")
        expected_company = extracted_data.get("company")

        if not invoice_number or expected_amount is None or not expected_due_date:
            return False, {
                "verified": False,
                "reason": "Missing extracted invoice attributes required for verification.",
                "extracted_data": extracted_data
            }

        logger.info(f"Running independent verification for {invoice_number} (Amount: {expected_amount}, Due: {expected_due_date})")
        
        result = FinanceService.verify_invoice_record(
            db=db,
            invoice_number=invoice_number,
            expected_amount=float(expected_amount),
            expected_due_date=str(expected_due_date),
            expected_company=expected_company,
            simulate_verification_failure=simulate_verification_failure
        )
        
        return result["verified"], result
