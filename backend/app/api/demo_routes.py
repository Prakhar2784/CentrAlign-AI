from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.agent.orchestrator import AgentOrchestrator
from app.services.seed_data import reset_database_to_initial

router = APIRouter(prefix="/api/demo", tags=["Demo Scenarios"])

@router.post("/scenario-1-success", summary="Demo Scenario 1: Successful End-to-End Execution")
def run_scenario_1(db: Session = Depends(get_db)):
    reset_database_to_initial(db)
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    state = orchestrator.execute_task(db=db, user_goal=goal)
    return {
        "scenario": "Scenario 1: Successful Execution",
        "description": "Standard flow finding latest Acme Corp invoice (INV-1003), updating finance ledger, and verifying state.",
        "state": state
    }

@router.post("/scenario-2-retry", summary="Demo Scenario 2: Transient Failure & Self-Healing Retry")
def run_scenario_2(db: Session = Depends(get_db)):
    reset_database_to_initial(db)
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    # Simulate DB lock failure on first update attempt
    state = orchestrator.execute_task(
        db=db,
        user_goal=goal,
        simulation_context={"fail_first_update": True}
    )
    return {
        "scenario": "Scenario 2: Failure & Recovery",
        "description": "First update fails with simulated DB lock (503), agent observes error, evaluates retry, retries, and successfully verifies.",
        "state": state
    }

@router.post("/scenario-3-verification-fail", summary="Demo Scenario 3: Verification Failure Detection")
def run_scenario_3(db: Session = Depends(get_db)):
    reset_database_to_initial(db)
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    # Simulate verification mismatch
    state = orchestrator.execute_task(
        db=db,
        user_goal=goal,
        simulation_context={"fail_verification": True}
    )
    return {
        "scenario": "Scenario 3: Verification Failure",
        "description": "Verifies that agent does NOT claim false success when verification detects an integrity mismatch.",
        "state": state
    }

@router.post("/scenario-4-generalization", summary="Demo Scenario 4: Multi-Company Generalization (Globex)")
def run_scenario_4(db: Session = Depends(get_db)):
    reset_database_to_initial(db)
    orchestrator = AgentOrchestrator()
    goal = "Find the latest invoice from Globex, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    state = orchestrator.execute_task(db=db, user_goal=goal)
    return {
        "scenario": "Scenario 4: Multi-Company Generalization",
        "description": "Proves the agent seamlessly handles Globex without hardcoded company logic.",
        "state": state
    }
