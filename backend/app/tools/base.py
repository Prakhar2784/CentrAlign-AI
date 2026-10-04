from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    retryable: bool = False
    is_mutation: bool = False

class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]
    is_mutation: bool = False

    @abstractmethod
    def execute(self, db: Session, **kwargs) -> ToolResult:
        """Execute the tool with database session and provided arguments."""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON schema format compatible with function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
