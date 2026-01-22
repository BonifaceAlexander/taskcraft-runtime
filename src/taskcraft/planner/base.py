from typing import List, Protocol, Dict, Any
from taskcraft.state.models import Task

class Planner(Protocol):
    """
    Abstract interface for an Agent's brain (Strategy Pattern).
    
    TaskCraft is **model-agnostic**. While we provide a first-class `GeminiPlanner`,
    implementation can be swappped for:
    1. Other LLMs (Claude, GPT-4)
    2. Local Models (Llama 3 via Ollama)
    3. Symbolic AI / Tree of Thoughts
    4. Hardcoded Scripts (DummyPlanner)
    
    The Runtime does not care *how* the plan is generated, only *what* the next step is.
    """
    async def plan(self, task: Task, history: List[Dict[str, str]]) -> Any:
        ...
