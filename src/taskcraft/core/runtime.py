import asyncio
from typing import List, Dict, Any, Callable
from datetime import datetime
import structlog

from taskcraft.core.lifecycle import AgentState, StepStatus
from taskcraft.state.models import Task, Step
from taskcraft.state.persistence import StateManager, SQLiteStateManager
from taskcraft.governance.policy import PolicyEngine, PolicyDecision

logger = structlog.get_logger()

class AgentRuntime:
    def __init__(self, 
                 state_manager: StateManager,
                 policy_engine: PolicyEngine,
                 tools: Dict[str, Callable]):
        self.state_manager = state_manager
        self.policy_engine = policy_engine
        self.tools = tools

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

    async def execute_step(self, task: Task, action: str, params: dict) -> Dict[str, Any]:
        """Executes a single step with governance checks. Returns the result."""
        # 1. Update State
        step = Step(task_id=task.task_id, index=task.current_step_index, name=action, input_data=params)
        task.steps.append(step)
        task.current_step_index += 1
        task.updated_at = datetime.now()
        
        # 2. Check Governance
        context = {'action_count': len(task.steps)}
        decision = self.policy_engine.evaluate(action, params, context)
        
        if not decision.allowed:
            if decision.requires_approval:
                task.status = AgentState.AWAITING_APPROVAL
                step.status = "PENDING_APPROVAL"
                logger.info("Task halted for approval", task_id=task.task_id, action=action)
                await self.state_manager.save_task(task)
                return {"status": "HALTED", "reason": "Approval Required"}
            else:
                task.status = AgentState.FAILED
                step.status = "BLOCKED"
                step.error = decision.reason
                logger.warn("Action blocked by policy", task_id=task.task_id, action=action, reason=decision.reason)
                await self.state_manager.save_task(task)
                return {"status": "BLOCKED", "reason": decision.reason}

        # 3. Execute
        task.status = AgentState.EXECUTING
        step.status = "RUNNING"
        step.start_time = datetime.now()
        await self.state_manager.save_task(task)

        try:
            logger.info("Executing action", action=action)
            if action in self.tools:
                result = await self.tools[action](**params)
            else:
                raise ValueError(f"Tool {action} not found")
            
            step.output_data = {"result": result}
            step.status = "COMPLETED"
            return {"status": "SUCCESS", "output": result}
        except Exception as e:
            step.status = "FAILED"
            step.error = str(e)
            logger.error("Step execution failed", error=e)
            return {"status": "ERROR", "error": str(e)}
        finally:
            step.end_time = datetime.now()
            task.updated_at = datetime.now()
            await self.state_manager.save_task(task)

    async def run_loop(self, task: Task, llm_client: Any):
        """
        Main execution loop.
        Queries LLM -> logic -> Execute Step -> Repeat.
        """
        from taskcraft.core.lifecycle import AgentState
        
        logger.info("Starting run loop", task_id=task.task_id)
        
        while task.status not in [AgentState.COMPLETED, AgentState.FAILED, AgentState.TERMINATED, AgentState.AWAITING_APPROVAL]:
            # 1. Construct History (Simplified)
            # In a real system, we'd format all previous steps as chat history
            history = [{"role": "user", "content": task.description}]
            for s in task.steps:
                history.append({"role": "model", "content": f"Call {s.name}({s.input_data})"})
                if s.status == "COMPLETED":
                    history.append({"role": "function", "name": s.name, "content": str(s.output_data)})
            
            # 2. Call LLM
            logger.info("Querying LLM...")
            # Note: We are passing just the description + history. 
            # Real impl would pass the `tools` definition to the LLM.
            response = await llm_client.generate_response(history=history)
            
            # 3. Parse Response (Mock logic for MVP since we don't have real tool parsing yet)
            # We assume for this demo that the LLM returns text, or we force a tool call for the demo.
            text = response.text
            logger.info("LLM Response", text=text)

            # STOP Condition (Mock)
            if "DONE" in text:
                task.status = AgentState.COMPLETED
                break
            
            # For the demo, we won't implement the full complex parsing loop here yet 
            # because we need the parsed function call from the `response` object.
            # We will rely on the `main_cli` to invoke specific steps or a smarter client.
            # But to satisfy the user request "Connect real Gemini tool calls",
            # we need to inspect `response.parts`.
            
            # Result processing
            tool_executed = False
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if fn := part.function_call:
                        print(f"🤖 Agent wants to call: {fn.name}")
                        result = await self.execute_step(task, fn.name, dict(fn.args))
                        tool_executed = True
                        if result.get("status") == "HALTED":
                            return # Exit loop to wait for approval
            
            if tool_executed:
                continue

            # If no tool call, treating as thought/comment
            # Just loop or break? For MVP, let's break to avoid infinite loops if no tool called.
            logger.info("No tool call detected, waiting for user input (interactive mode not fully impl).")
            break
            
        await self.state_manager.save_task(task)
