from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.tools.base import BaseTool, ToolResult
from app.services.finance_service import FinanceService
from app.core.config import settings

class SearchFinanceRecordsTool(BaseTool):
    name = "search_finance_records"
    description = "Search the internal finance system ledger for records by company name or invoice number."
    is_mutation = False
    parameters = {
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name to query in the finance ledger (e.g., 'Acme Corp', 'Globex')."
            },
            "invoice_number": {
                "type": "string",
                "description": "Invoice number to query (e.g. 'INV-1003')."
            }
        },
        "required": []
    }

    def execute(self, db: Session, company: Optional[str] = None, invoice_number: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            records = FinanceService.search_records(db, company=company, invoice_number=invoice_number)
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "total_found": len(records),
                    "records": records
                },
                is_mutation=False
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Error searching finance records: {str(e)}",
                is_mutation=False
            )


class UpdateInvoiceRecordTool(BaseTool):
    name = "update_invoice_record"
    description = (
        "Update or sync an invoice record in the internal finance system with its validated "
        "amount, due_date, company name, and optional notes."
    )
    is_mutation = True
    parameters = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice number to update (e.g., 'INV-1003')."
            },
            "amount": {
                "type": "number",
                "description": "The exact monetary amount extracted from the invoice."
            },
            "due_date": {
                "type": "string",
                "description": "Payment due date in YYYY-MM-DD format (e.g., '2026-10-15')."
            },
            "company": {
                "type": "string",
                "description": "The company / vendor name (e.g. 'Acme Corp')."
            },
            "notes": {
                "type": "string",
                "description": "Optional notes or audit context."
            }
        },
        "required": ["invoice_number", "amount", "due_date"]
    }

    def execute(
        self,
        db: Session,
        invoice_number: str,
        amount: float,
        due_date: str,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        simulate_failure: bool = False,
        **kwargs
    ) -> ToolResult:
        try:
            # Check if global config or kwargs triggers failure simulation
            should_fail = simulate_failure or settings.FAIL_FIRST_UPDATE
            
            res = FinanceService.update_invoice_record(
                db=db,
                invoice_number=invoice_number,
                amount=amount,
                due_date=due_date,
                company=company,
                notes=notes,
                simulate_failure=should_fail
            )
            
            if not res["success"]:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=res["error"],
                    retryable=res.get("retryable", True),
                    is_mutation=True
                )
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                data=res,
                is_mutation=True
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Unexpected error updating invoice record: {str(e)}",
                retryable=True,
                is_mutation=True
            )


class VerifyInvoiceRecordTool(BaseTool):
    name = "verify_invoice_record"
    description = (
        "Independently read back an invoice record from the internal finance system and verify that "
        "the persisted amount, due date, and company strictly match expected values."
    )
    is_mutation = False
    parameters = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "The invoice number to verify in the finance ledger (e.g. 'INV-1003')."
            },
            "expected_amount": {
                "type": "number",
                "description": "The expected amount that should be persisted."
            },
            "expected_due_date": {
                "type": "string",
                "description": "The expected due date (YYYY-MM-DD) that should be persisted."
            },
            "expected_company": {
                "type": "string",
                "description": "The expected company name."
            }
        },
        "required": ["invoice_number", "expected_amount", "expected_due_date"]
    }

    def execute(
        self,
        db: Session,
        invoice_number: str,
        expected_amount: float,
        expected_due_date: str,
        expected_company: Optional[str] = None,
        simulate_verification_failure: bool = False,
        **kwargs
    ) -> ToolResult:
        try:
            should_fail_verification = simulate_verification_failure or settings.FAIL_VERIFICATION
            res = FinanceService.verify_invoice_record(
                db=db,
                invoice_number=invoice_number,
                expected_amount=expected_amount,
                expected_due_date=expected_due_date,
                expected_company=expected_company,
                simulate_verification_failure=should_fail_verification
            )
            
            if not res["verified"]:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=res.get("reason", "Verification failed due to data discrepancy."),
                    data=res,
                    retryable=False,
                    is_mutation=False
                )
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                data=res,
                is_mutation=False
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Error executing verification tool: {str(e)}",
                is_mutation=False
            )
