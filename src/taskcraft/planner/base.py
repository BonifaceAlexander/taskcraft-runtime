from typing import List, Protocol, Dict, Any
from taskcraft.state.models import Task

class Planner(Protocol):
    """
    Abstract interface for an Agent's brain.
    Responsible for taking context and deciding the next step.
    """
    async def plan(self, task: Task, history: List[Dict[str, str]]) -> Any:
        ...
