from typing import List, Dict, Any
from taskcraft.planner.base import Planner
from taskcraft.state.models import Task

class DummyPlanner(Planner):
    """
    A dumb planner that follows a hardcoded script.
    Demonstrates that TaskCraft is model-agnostic; you can plug in *anything* 
    that satisfies the Planner interface, even a static script or a decision tree.
    """
    
    def __init__(self, script: List[str] = None):
        # A list of tool calls to make in order
        self.script = script or []
        self._step_index = 0

    async def plan(self, task: Task, history: List[Dict[str, str]]) -> Any:
        class MockResponse:
            def __init__(self, text): 
                self.text = text
                self.parts = [] # No function calls in this simple mock unless we enhance it

        if self._step_index < len(self.script):
            action = self.script[self._step_index]
            self._step_index += 1
            return MockResponse(text=f"I will execute: {action}")
        
        return MockResponse(text="I am done.")
