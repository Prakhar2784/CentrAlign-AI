from typing import List
from app.agent.state import AgentPlanStep

class TaskPlanner:
    """
    Formulates a structured execution plan for autonomous invoice processing.
    """
    
    @staticmethod
    def create_initial_plan(user_goal: str) -> List[AgentPlanStep]:
        return [
            AgentPlanStep(
                step_number=1,
                description="Search invoice portal for target company documents",
                status="PENDING"
            ),
            AgentPlanStep(
                step_number=2,
                description="Evaluate candidate invoices and retrieve the latest document",
                status="PENDING"
            ),
            AgentPlanStep(
                step_number=3,
                description="Extract invoice number, total amount, due date, and currency",
                status="PENDING"
            ),
            AgentPlanStep(
                step_number=4,
                description="Search internal finance system for matching ledger entry",
                status="PENDING"
            ),
            AgentPlanStep(
                step_number=5,
                description="Update finance ledger with extracted amount and due date",
                status="PENDING"
            ),
            AgentPlanStep(
                step_number=6,
                description="Independently verify stored finance record against expected values",
                status="PENDING"
            )
        ]
