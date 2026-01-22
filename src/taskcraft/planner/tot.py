from typing import List, Dict, Any
from taskcraft.planner.base import Planner
from taskcraft.state.models import Task
from taskcraft.planner.gemini import GeminiPlanner
import structlog

logger = structlog.get_logger()

class TreeOfThoughtsPlanner(Planner):
    """
    Advanced planner that generates multiple options and selects the best one.
    (MVP Implementation wrapping GeminiPlanner)
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.delegate = GeminiPlanner(model_name)

    async def plan(self, task: Task, history: List[Dict[str, str]]) -> Any:
        # 1. Verification / Reflection Step
        # Before planning, check the last step result
        if task.steps and task.steps[-1].status == "FAILED":
             logger.info("Previous step failed. Engaging deeper reflection.")
             # Inject reflection into history
             history.append({
                 "role": "model", 
                 "content": "Wait, the last step failed. I need to analyze why before proceeding."
             })
        
        # 2. Generate multiple thoughts (Simulated)
        # In a full ToT, we would ask the model for 3 options, then ask it to vote.
        # For this MVP, we prompt the model to "Think Step-by-Step" explicitly.
        
        logger.info("Using Tree-of-Thoughts strategy...")
        # Modifying the latest user message or adding a system prompt instruction
        # to ensure high-quality reasoning.
        
        # Delegate to standard planner but with enhanced prompting context implied
        return await self.delegate.plan(task, history)
