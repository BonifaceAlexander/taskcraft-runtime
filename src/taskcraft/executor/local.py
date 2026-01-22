import structlog
from typing import Dict, Callable, Any
from datetime import datetime
from taskcraft.executor.base import Executor

logger = structlog.get_logger()

class LocalExecutor(Executor):
    """
    Executes tools in the current process. 
    Best for local tasks (file organizing) or simple agents.
    """
    def __init__(self, tools: Dict[str, Callable]):
        self.tools = tools

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool by name with the given parameters.
        """
        logger.info("Executing tool locally", tool=tool_name)
        
        if tool_name not in self.tools:
            logger.error("Tool not found", tool=tool_name)
            raise ValueError(f"Tool {tool_name} not found")
            
        try:
            # Execute
            func = self.tools[tool_name]
            result = await func(**params)
            
            return {
                "status": "SUCCESS",
                "output": result
            }
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return {
                "status": "ERROR",
                "error": str(e)
            }
