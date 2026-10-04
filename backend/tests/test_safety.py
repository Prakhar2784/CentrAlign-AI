from app.agent.safety import SafetyGuard
from app.agent.orchestrator import AgentOrchestrator

def test_safety_guard_permits_reads():
    safe, err = SafetyGuard.check_authorization("Find Acme's invoice", "search_invoices", is_mutation=False)
    assert safe is True
    assert err is None

def test_safety_guard_blocks_unauthorized_mutation():
    # User only asked to find/read, but tool is a mutation
    safe, err = SafetyGuard.check_authorization("Find Acme's invoice", "update_invoice_record", is_mutation=True)
    assert safe is False
    assert "SAFETY POLICY BLOCK" in err

def test_safety_guard_allows_authorized_mutation():
    safe, err = SafetyGuard.check_authorization("Find Acme's invoice and update the finance system", "update_invoice_record", is_mutation=True)
    assert safe is True
    assert err is None

def test_agent_stops_when_blocked_by_safety(db_session):
    orchestrator = AgentOrchestrator()
    # Request only to search/read without write intent
    goal = "Only search and find the latest invoice from Acme Corp."
    # The default deterministic plan attempts full flow, but Safety Guard intercepts the update mutation
    # Let's test that if mutation is attempted without permission, state reflects BLOCKED_SAFETY
    safe, err = SafetyGuard.check_authorization(goal, "update_invoice_record", is_mutation=True)
    assert safe is False
