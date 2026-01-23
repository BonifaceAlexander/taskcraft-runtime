import structlog
from datetime import datetime
from typing import Dict, Any, Callable

from taskcraft.core.lifecycle import AgentState
from taskcraft.state.models import Task, Step
from taskcraft.state.persistence import StateManager
from taskcraft.governance.policy import PolicyEngine
from taskcraft.planner.base import Planner
from taskcraft.executor.base import Executor

logger = structlog.get_logger()

class AgentRuntime:
    """
    Core Runtime Logic.
    Orchestrates the ReAct loop:
    1. Observe (Load Task)
    2. Plan (Call Planner)
    3. Govern (Check Policy)
    4. Act (Call Executor)
    5. Reflect (Save State)
    """
    def __init__(self, 
                 state_manager: StateManager,
                 policy_engine: PolicyEngine,
                 executor: Executor):
        self.state_manager = state_manager
        self.policy_engine = policy_engine
        self.executor = executor

    async def create_task(self, description: str) -> Task:
        """Starts a new agent task."""
        task = Task(description=description, status=AgentState.PLANNING)
        await self.state_manager.save_task(task)
        logger.info("Task created", task_id=task.task_id)
        return task

    async def resume_task(self, task_id: str) -> Task:
        """Resumes an existing task."""
        task = await self.state_manager.load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        logger.info("Task resumed", task_id=task.task_id, status=task.status)
        return task

    async def run_loop(self, task: Task, planner: Planner):
        """
        Main execution loop.
        """
        logger.info("Starting run loop", task_id=task.task_id)
        
        while task.status not in [AgentState.COMPLETED, AgentState.FAILED, AgentState.TERMINATED, AgentState.AWAITING_APPROVAL]:
            # 1. Plan
            history = self._build_history(task)
            plan_response = await planner.plan(task, history)
            
            # 2. Parse (Logic similar to before, handling text vs tool)
            if hasattr(plan_response, 'text') and plan_response.text:
                if "DONE" in plan_response.text:
                    task.status = AgentState.COMPLETED
                    await self.state_manager.save_task(task)
                    break
            
            tool_executed = False
            # Check for tool calls
            if hasattr(plan_response, 'parts'):
                for part in plan_response.parts:
                    if fn := part.function_call:
                        # 3. Govern & 4. Act
                        result = await self._execute_governed_step(task, fn.name, dict(fn.args))
                        tool_executed = True
                        if result["status"] == "HALTED":
                            return # Exit for approval

            # Check for thought (Text only)
            if not tool_executed and hasattr(plan_response, 'text') and plan_response.text:
                await self._record_thought(task, plan_response.text)
                continue

            if not tool_executed:
                 logger.info("No tool call or thought. Stopping.")
                 break
            
        await self.state_manager.save_task(task)

    async def execute_step(self, task: Task, action: str, params: dict, bypass_policy: bool = False) -> Dict[str, Any]:
        """Exposed for Manual Approval / CLI to run a specific step."""
        return await self._execute_governed_step(task, action, params, bypass_policy=bypass_policy)

    async def _execute_governed_step(self, task: Task, action: str, params: dict, bypass_policy: bool = False) -> Dict[str, Any]:
        """Internal method to handle policy + execution."""
        # Update State
        step = Step(task_id=task.task_id, index=task.current_step_index, name=action, input_data=params)
        task.steps.append(step)
        task.current_step_index += 1
        
        # Check Governance
        if bypass_policy:
            decision = type('Decision', (), {'allowed': True, 'requires_approval': False})() # Mock allowed decision
        else:
            context = {'action_count': len(task.steps)}
            decision = self.policy_engine.evaluate(action, params, context)
        
        if not decision.allowed:
            if decision.requires_approval:
                task.status = AgentState.AWAITING_APPROVAL
                step.status = "PENDING_APPROVAL"
                await self.state_manager.save_task(task)
                logger.info("Task halted for approval", task_id=task.task_id, action=action)
                return {"status": "HALTED", "reason": "Approval Required"}
            else:
                task.status = AgentState.FAILED
                step.status = "BLOCKED"
                step.error = decision.reason
                await self.state_manager.save_task(task)
                logger.warn("Action blocked", task_id=task.task_id, action=action)
                return {"status": "BLOCKED", "reason": decision.reason}

        # Execute
        task.status = AgentState.EXECUTING
        step.status = "RUNNING"
        step.start_time = datetime.now()
        await self.state_manager.save_task(task)

        # Delegate to Executor
        result = await self.executor.execute(action, params)
        
        if result["status"] == "SUCCESS":
            step.output_data = {"result": result["output"]}
            step.status = "COMPLETED"
            step.end_time = datetime.now()
            task.updated_at = datetime.now()
            await self.state_manager.save_task(task)
            return {"status": "SUCCESS", "output": result["output"]}
        else:
            step.status = "FAILED"
            step.error = result["error"]
            step.end_time = datetime.now()
            task.updated_at = datetime.now()
            await self.state_manager.save_task(task)
            return {"status": "FAILED", "error": result["error"]}

    async def _record_thought(self, task: Task, thought: str):
        logger.info("Agent thought", content=thought[:100])
        step = Step(
            task_id=task.task_id,
            index=task.current_step_index,
            name="think",
            input_data={"thought": thought},
            status="COMPLETED",
            output_data={"result": "Thought recorded"}
        )
        task.steps.append(step)
        task.current_step_index += 1
        await self.state_manager.save_task(task)

    def _build_history(self, task: Task) -> list:
        history = [{"role": "user", "content": task.description}]
        for s in task.steps:
            if s.name == "think":
                 history.append({"role": "model", "content": s.input_data.get("thought", "")})
            else:
                history.append({"role": "model", "content": f"Call {s.name}({s.input_data})"})
                if s.status == "COMPLETED":
                    history.append({"role": "function", "name": s.name, "content": str(s.output_data)})
        return history
