from app.services.finance_service import FinanceService

def test_search_finance_records(db_session):
    records = FinanceService.search_records(db_session, company="Acme Corp")
    assert len(records) >= 3
    inv_nums = [r["invoice_number"] for r in records]
    assert "INV-1003" in inv_nums

def test_update_invoice_record_success(db_session):
    res = FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        company="Acme Corp"
    )
    assert res["success"] is True
    rec = FinanceService.get_record(db_session, "INV-1003")
    assert rec["amount"] == 48000.0
    assert rec["due_date"] == "2026-10-15"
    assert rec["sync_status"] == "SYNCED"

def test_update_invoice_record_simulated_failure(db_session):
    res = FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        simulate_failure=True
    )
    assert res["success"] is False
    assert "FINANCE_DB_LOCK_TIMEOUT" in res["error"]
    assert res["retryable"] is True

def test_verify_invoice_record_success(db_session):
    # First update
    FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        company="Acme Corp"
    )
    
    # Then verify
    ver = FinanceService.verify_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        expected_amount=48000.0,
        expected_due_date="2026-10-15",
        expected_company="Acme Corp"
    )
    assert ver["verified"] is True

def test_verify_invoice_record_discrepancy(db_session):
    # First update with 48000.0
    FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        company="Acme Corp"
    )
    
    # Try verifying with wrong amount
    ver = FinanceService.verify_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        expected_amount=99999.0,
        expected_due_date="2026-10-15"
    )
    assert ver["verified"] is False
    assert any("Amount mismatch" in d for d in ver["discrepancies"])
