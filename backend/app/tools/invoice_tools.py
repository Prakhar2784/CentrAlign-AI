import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.tools.base import BaseTool, ToolResult
from app.services.invoice_service import InvoiceService

class SearchInvoicesTool(BaseTool):
    name = "search_invoices"
    description = (
        "Search invoice portal records by company name, invoice number, or keyword. "
        "Returns a list of matching invoice records sorted by issue date descending."
    )
    is_mutation = False
    parameters = {
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company/vendor name to search for (e.g., 'Acme Corp', 'Globex', 'Initech', 'Umbrella')."
            },
            "query": {
                "type": "string",
                "description": "Optional keyword or invoice number filter."
            }
        },
        "required": []
    }

    def execute(self, db: Session, company: Optional[str] = None, query: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            results = InvoiceService.search_invoices(db, company=company, query=query)
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "total_found": len(results),
                    "invoices": results
                },
                is_mutation=False
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Failed searching invoices: {str(e)}",
                is_mutation=False
            )


class GetInvoiceTool(BaseTool):
    name = "get_invoice"
    description = "Retrieve full invoice details and raw document contents by invoice number (e.g., 'INV-1003')."
    is_mutation = False
    parameters = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "The exact invoice ID/number (e.g. 'INV-1003')."
            }
        },
        "required": ["invoice_number"]
    }

    def execute(self, db: Session, invoice_number: str, **kwargs) -> ToolResult:
        try:
            invoice = InvoiceService.get_invoice(db, invoice_number=invoice_number)
            if not invoice:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Invoice '{invoice_number}' not found in invoice portal.",
                    retryable=False,
                    is_mutation=False
                )
            return ToolResult(
                tool_name=self.name,
                success=True,
                data=invoice,
                is_mutation=False
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Error retrieving invoice: {str(e)}",
                is_mutation=False
            )


class ExtractInvoiceDataTool(BaseTool):
    name = "extract_invoice_data"
    description = (
        "Extract structured financial entities (invoice_number, company, amount, due_date, issue_date, currency) "
        "from an invoice record or document text."
    )
    is_mutation = False
    parameters = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "The invoice number to extract data for."
            },
            "document_text": {
                "type": "string",
                "description": "Optional raw document content text if already retrieved."
            }
        },
        "required": ["invoice_number"]
    }

    def execute(self, db: Session, invoice_number: str, document_text: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            inv = InvoiceService.get_invoice(db, invoice_number=invoice_number)
            if inv:
                extracted = {
                    "invoice_number": inv["invoice_number"],
                    "company": inv["company"],
                    "amount": float(inv["amount"]),
                    "due_date": inv["due_date"],
                    "issue_date": inv["issue_date"],
                    "currency": inv.get("currency", "USD"),
                    "status": inv.get("status", "ISSUED")
                }
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data=extracted,
                    is_mutation=False
                )
            
            # Fallback regex parsing if text was passed directly
            if document_text:
                extracted = self._parse_from_text(document_text, invoice_number)
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data=extracted,
                    is_mutation=False
                )

            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Could not extract data for invoice '{invoice_number}': invoice not found.",
                is_mutation=False
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Failed extracting invoice data: {str(e)}",
                is_mutation=False
            )

    def _parse_from_text(self, text: str, default_inv_num: str) -> Dict[str, Any]:
        amount_match = re.search(r"TOTAL DUE:?\s*\$?([\d,]+\.?\d*)", text, re.IGNORECASE)
        amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0
        
        due_match = re.search(r"DUE DATE:?\s*([\d-]+)", text, re.IGNORECASE)
        due_date = due_match.group(1) if due_match else None
        
        company_match = re.search(r"VENDOR:?\s*([^|\n]+)", text, re.IGNORECASE)
        company = company_match.group(1).strip() if company_match else "Unknown"

        return {
            "invoice_number": default_inv_num,
            "company": company,
            "amount": amount,
            "due_date": due_date,
            "currency": "USD"
        }
