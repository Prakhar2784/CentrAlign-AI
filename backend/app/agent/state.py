from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utcnow_str():
    return datetime.now(timezone.utc).isoformat()

class AgentPlanStep(BaseModel):
    step_number: int
    description: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED

class AgentStepLog(BaseModel):
    step_index: int
    timestamp: str = Field(default_factory=utcnow_str)
    thought: str
    action: str
    tool_name: Optional[str] = None
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    tool_result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    retry_count: int = 0
    duration_ms: float = 0.0

class AgentState(BaseModel):
    task_id: str
    user_goal: str
    status: str = "INITIALIZING"  # INITIALIZING, PLANNING, EXECUTING, VERIFYING, COMPLETED, FAILED, BLOCKED_SAFETY
    plan: List[AgentPlanStep] = Field(default_factory=list)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    logs: List[AgentStepLog] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    is_safety_cleared: bool = True
    safety_message: Optional[str] = None
    verification_passed: bool = False
    verification_details: Optional[Dict[str, Any]] = None
    final_summary: Optional[str] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_str)
    updated_at: str = Field(default_factory=utcnow_str)

    def add_log(self, log: AgentStepLog):
        self.logs.append(log)
        self.updated_at = utcnow_str()

    def update_plan_status(self, step_number: int, status: str):
        for step in self.plan:
            if step.step_number == step_number:
                step.status = status
        self.updated_at = utcnow_str()
