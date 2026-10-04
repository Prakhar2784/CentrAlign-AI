from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def utcnow_str():
    return datetime.now(timezone.utc).isoformat()

class AgentMemory:
    """
    Explicit, inspectable short-term memory tracking:
    - User goal and constraints
    - Observations history
    - Entity scratchpad (extracted invoice info, record IDs)
    - Action counter and retry tracker
    """
    def __init__(self, user_goal: str):
        self.user_goal: str = user_goal
        self.observations: List[Dict[str, Any]] = []
        self.scratchpad: Dict[str, Any] = {}
        self.retries: Dict[str, int] = {}
        self.created_at: str = utcnow_str()

    def add_observation(self, tool_name: str, input_args: Dict[str, Any], result: Any, success: bool):
        self.observations.append({
            "tool_name": tool_name,
            "input_args": input_args,
            "result": result,
            "success": success,
            "timestamp": utcnow_str()
        })

    def store_entity(self, key: str, value: Any):
        self.scratchpad[key] = value

    def get_entity(self, key: str, default: Any = None) -> Any:
        return self.scratchpad.get(key, default)

    def record_retry(self, tool_name: str) -> int:
        self.retries[tool_name] = self.retries.get(tool_name, 0) + 1
        return self.retries[tool_name]

    def get_retry_count(self, tool_name: str) -> int:
        return self.retries.get(tool_name, 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_goal": self.user_goal,
            "observations_count": len(self.observations),
            "scratchpad": self.scratchpad,
            "retries": self.retries
        }
