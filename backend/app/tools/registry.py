import time
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.tools.base import BaseTool, ToolResult
from app.tools.invoice_tools import SearchInvoicesTool, GetInvoiceTool, ExtractInvoiceDataTool
from app.tools.finance_tools import SearchFinanceRecordsTool, UpdateInvoiceRecordTool, VerifyInvoiceRecordTool
from app.core.logging import logger

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            SearchInvoicesTool(),
            GetInvoiceTool(),
            ExtractInvoiceDataTool(),
            SearchFinanceRecordsTool(),
            UpdateInvoiceRecordTool(),
            VerifyInvoiceRecordTool()
        ]
        for tool in tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    def execute_tool(self, tool_name: str, db: Session, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not registered in ToolRegistry.",
                is_mutation=False
            )

        start_time = time.time()
        logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
        
        # Merge context if provided (e.g., demo simulation flags)
        exec_kwargs = dict(arguments)
        if context:
            exec_kwargs.update(context)

        try:
            result = tool.execute(db=db, **exec_kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.info(f"Tool '{tool_name}' completed in {duration_ms}ms with success={result.success}")
            return result
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Tool '{tool_name}' raised unhandled exception after {duration_ms}ms: {str(e)}")
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Unhandled tool execution error: {str(e)}",
                is_mutation=tool.is_mutation
            )

# Global default tool registry
default_tool_registry = ToolRegistry()
