from app.agent.orchestrator import AgentOrchestrator
from app.services.finance_service import FinanceService

def test_failure_detection_and_retry_recovery(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    # Inject fail_first_update simulation
    state = orchestrator.execute_task(
        db=db_session,
        user_goal=goal,
        simulation_context={"fail_first_update": True}
    )
    
    # Check that retry occurred
    update_logs = [log for log in state.logs if log.tool_name == "update_invoice_record"]
    assert len(update_logs) == 2, "Agent should have attempted update twice (1 failure + 1 retry)"
    assert update_logs[0].success is False, "First update should fail"
    assert "FINANCE_DB_LOCK_TIMEOUT" in update_logs[0].error
    assert update_logs[1].success is True, "Second update (retry) should succeed"
    
    # Final state should still be completed with passed verification
    assert state.status == "COMPLETED"
    assert state.verification_passed is True
    
    # Persistence confirmed
    rec = FinanceService.get_record(db_session, "INV-1003")
    assert rec["amount"] == 48000.0
