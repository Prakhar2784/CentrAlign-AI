from app.agent.orchestrator import AgentOrchestrator
from app.agent.verifier import TaskVerifier
from app.services.finance_service import FinanceService

def test_verifier_direct(db_session):
    # Prepare data in DB
    FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=48000.0,
        due_date="2026-10-15",
        company="Acme Corp"
    )
    
    # Valid verification
    passed, res = TaskVerifier.verify_persisted_state(
        db=db_session,
        extracted_data={
            "invoice_number": "INV-1003",
            "amount": 48000.0,
            "due_date": "2026-10-15",
            "company": "Acme Corp"
        }
    )
    assert passed is True
    assert res["verified"] is True

def test_verifier_detects_tampered_or_invalid_state(db_session):
    # Intentionally corrupt data in DB
    FinanceService.update_invoice_record(
        db=db_session,
        invoice_number="INV-1003",
        amount=1000.0,  # Wrong amount!
        due_date="2026-10-15"
    )
    
    passed, res = TaskVerifier.verify_persisted_state(
        db=db_session,
        extracted_data={
            "invoice_number": "INV-1003",
            "amount": 48000.0,
            "due_date": "2026-10-15",
            "company": "Acme Corp"
        }
    )
    assert passed is False
    assert res["verified"] is False
    assert "Amount mismatch" in str(res.get("discrepancies"))

def test_agent_reports_failure_when_verification_fails(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    # Inject verification failure trigger
    state = orchestrator.execute_task(
        db=db_session,
        user_goal=goal,
        simulation_context={"fail_verification": True}
    )
    
    assert state.status == "FAILED"
    assert state.verification_passed is False
    assert "Verification FAILED" in (state.final_summary or "")
