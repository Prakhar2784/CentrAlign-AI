from app.tools.invoice_tools import SearchInvoicesTool, GetInvoiceTool, ExtractInvoiceDataTool
from app.tools.finance_tools import SearchFinanceRecordsTool, UpdateInvoiceRecordTool, VerifyInvoiceRecordTool
from app.tools.registry import default_tool_registry

def test_search_invoices_tool(db_session):
    tool = SearchInvoicesTool()
    res = tool.execute(db=db_session, company="Acme Corp")
    assert res.success is True
    assert res.data["total_found"] == 3
    assert res.data["invoices"][0]["invoice_number"] == "INV-1003"

def test_get_invoice_tool(db_session):
    tool = GetInvoiceTool()
    res = tool.execute(db=db_session, invoice_number="INV-1003")
    assert res.success is True
    assert res.data["amount"] == 48000.0

def test_extract_invoice_data_tool(db_session):
    tool = ExtractInvoiceDataTool()
    res = tool.execute(db=db_session, invoice_number="INV-1003")
    assert res.success is True
    assert res.data["invoice_number"] == "INV-1003"
    assert res.data["company"] == "Acme Corp"
    assert res.data["amount"] == 48000.0
    assert res.data["due_date"] == "2026-10-15"

def test_finance_tools_integration(db_session):
    search_tool = SearchFinanceRecordsTool()
    update_tool = UpdateInvoiceRecordTool()
    verify_tool = VerifyInvoiceRecordTool()

    # 1. Search
    s_res = search_tool.execute(db=db_session, company="Acme Corp")
    assert s_res.success is True

    # 2. Update
    u_res = update_tool.execute(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        company="Acme Corp"
    )
    assert u_res.success is True

    # 3. Verify
    v_res = verify_tool.execute(
        db=db_session,
        invoice_number="INV-1003",
        expected_amount=48000.0,
        expected_due_date="2026-10-15"
    )
    assert v_res.success is True

def test_tool_registry_schemas():
    schemas = default_tool_registry.get_schemas()
    assert len(schemas) >= 6
    names = [s["name"] for s in schemas]
    assert "search_invoices" in names
    assert "get_invoice" in names
    assert "extract_invoice_data" in names
    assert "search_finance_records" in names
    assert "update_invoice_record" in names
    assert "verify_invoice_record" in names
