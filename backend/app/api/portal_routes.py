from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.services.invoice_service import InvoiceService
from app.services.finance_service import FinanceService
from app.services.seed_data import reset_database_to_initial

router = APIRouter(prefix="/api", tags=["Simulated Portals"])

@router.get("/portal/invoices", summary="List simulated portal invoices")
def list_portal_invoices(company: Optional[str] = None, db: Session = Depends(get_db)):
    if company:
        return InvoiceService.search_invoices(db, company=company)
    return InvoiceService.list_all(db)

@router.get("/portal/invoices/{invoice_number}", summary="Get portal invoice by number")
def get_portal_invoice(invoice_number: str, db: Session = Depends(get_db)):
    inv = InvoiceService.get_invoice(db, invoice_number=invoice_number)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv

@router.get("/finance/records", summary="List internal finance records")
def list_finance_records(company: Optional[str] = None, db: Session = Depends(get_db)):
    if company:
        return FinanceService.search_records(db, company=company)
    return FinanceService.list_all(db)

@router.get("/finance/records/{invoice_number}", summary="Get internal finance record by invoice number")
def get_finance_record(invoice_number: str, db: Session = Depends(get_db)):
    rec = FinanceService.get_record(db, invoice_number=invoice_number)
    if not rec:
        raise HTTPException(status_code=404, detail="Finance record not found")
    return rec

@router.post("/system/reset", summary="Reset simulated database to clean initial state")
def reset_system(db: Session = Depends(get_db)):
    reset_database_to_initial(db)
    return {"status": "success", "message": "Simulated invoice portal and finance ledger reset to initial state."}
