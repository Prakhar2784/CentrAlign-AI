import re
from typing import Tuple, Optional
from app.core.logging import logger

class SafetyGuard:
    """
    Evaluates action authorization:
    - Read-only actions (search, get, extract, inspect) are always safe to run.
    - Mutation actions (update_invoice_record, write) require explicit user intent or authorization.
    """
    
    WRITE_KEYWORDS = ["update", "sync", "enter", "modify", "save", "insert", "write", "post", "record"]

    @classmethod
    def check_authorization(cls, user_goal: str, action_name: str, is_mutation: bool) -> Tuple[bool, Optional[str]]:
        if not is_mutation:
            return True, None

        # Check if user prompt authorized mutation
        lower_goal = user_goal.lower()
        has_write_intent = any(re.search(rf"\b{kw}\b", lower_goal) for kw in cls.WRITE_KEYWORDS)
        
        if has_write_intent:
            return True, None

        # Mutation requested without user write intent
        msg = (
            f"SAFETY POLICY BLOCK: The tool '{action_name}' performs database modification, "
            f"but the original request '{user_goal}' only specified read-only actions. "
            f"Explicit confirmation or an updated prompt is required to authorize data modification."
        )
        logger.warning(msg)
        return False, msg
