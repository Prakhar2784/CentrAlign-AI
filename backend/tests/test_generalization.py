from app.agent.orchestrator import AgentOrchestrator
from app.services.finance_service import FinanceService

def test_generalization_globex(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Globex, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    state = orchestrator.execute_task(db=db_session, user_goal=goal)
    
    assert state.status == "COMPLETED"
    assert state.verification_passed is True
    # Latest invoice for Globex is INV-2002 ($64,000.00, due 2026-09-15)
    assert state.extracted_data.get("invoice_number") == "INV-2002"
    assert state.extracted_data.get("amount") == 64000.0
    assert state.extracted_data.get("due_date") == "2026-09-15"
    
    rec = FinanceService.get_record(db_session, "INV-2002")
    assert rec["amount"] == 64000.0
    assert rec["due_date"] == "2026-09-15"

def test_generalization_initech(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Initech, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    state = orchestrator.execute_task(db=db_session, user_goal=goal)
    
    assert state.status == "COMPLETED"
    assert state.verification_passed is True
    # Latest invoice for Initech is INV-3002 ($31,200.00, due 2026-08-30)
    assert state.extracted_data.get("invoice_number") == "INV-3002"
    assert state.extracted_data.get("amount") == 31200.0
    assert state.extracted_data.get("due_date") == "2026-08-30"

def test_generalization_umbrella(db_session):
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Umbrella, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    
    state = orchestrator.execute_task(db=db_session, user_goal=goal)
    
    assert state.status == "COMPLETED"
    assert state.verification_passed is True
    # Latest invoice for Umbrella is INV-4002 ($89,000.00, due 2026-10-01)
    assert state.extracted_data.get("invoice_number") == "INV-4002"
    assert state.extracted_data.get("amount") == 89000.0
    assert state.extracted_data.get("due_date") == "2026-10-01"
