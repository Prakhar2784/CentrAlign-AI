from app.services.invoice_service import InvoiceService

def test_search_invoices_by_company(db_session):
    results = InvoiceService.search_invoices(db_session, company="Acme Corp")
    assert len(results) == 3
    # Check issue dates are sorted descending
    dates = [inv["issue_date"] for inv in results]
    assert dates == sorted(dates, reverse=True)
    # The first element should be the latest invoice (INV-1003)
    assert results[0]["invoice_number"] == "INV-1003"
    assert results[0]["amount"] == 48000.0

def test_get_invoice_by_number(db_session):
    inv = InvoiceService.get_invoice(db_session, "INV-1003")
    assert inv is not None
    assert inv["invoice_number"] == "INV-1003"
    assert inv["company"] == "Acme Corp"
    assert inv["due_date"] == "2026-10-15"
    assert "Autonomous Agent Computing Nodes" in inv["raw_content"]

def test_get_nonexistent_invoice(db_session):
    inv = InvoiceService.get_invoice(db_session, "INV-9999")
    assert inv is None
