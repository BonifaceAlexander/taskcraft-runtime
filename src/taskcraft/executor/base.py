from typing import Dict, Any, Protocol

class Executor(Protocol):
    """
    Abstract interface for tool execution strategies.
    """
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        ...
