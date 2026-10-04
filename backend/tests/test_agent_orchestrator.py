from app.agent.orchestrator import AgentOrchestrator
from app.services.finance_service import FinanceService

def test_agent_orchestrator_successful_execution(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    state = orchestrator.execute_task(db=db_session, user_goal=goal)
    
    assert state.status == "COMPLETED"
    assert state.verification_passed is True
    assert state.extracted_data.get("invoice_number") == "INV-1003"
    assert state.extracted_data.get("amount") == 48000.0
    assert state.extracted_data.get("due_date") == "2026-10-15"
    assert len(state.logs) >= 6
    
    # Assert database persistence
    rec = FinanceService.get_record(db_session, "INV-1003")
    assert rec["amount"] == 48000.0
    assert rec["due_date"] == "2026-10-15"
    assert rec["sync_status"] == "SYNCED"

def test_agent_does_not_claim_success_before_verification(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    # Verify tool execution order in step logs
    state = orchestrator.execute_task(db=db_session, user_goal=goal)
    
    tool_sequence = [log.tool_name for log in state.logs if log.tool_name]
    assert "update_invoice_record" in tool_sequence
    assert "verify_invoice_record" in tool_sequence
    
    update_idx = tool_sequence.index("update_invoice_record")
    verify_idx = tool_sequence.index("verify_invoice_record")
    
    # Verification must happen AFTER update
    assert verify_idx > update_idx
    # Final step must be after verification
    assert state.logs[-1].step_index > state.logs[verify_idx].step_index
