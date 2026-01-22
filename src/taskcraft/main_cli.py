import argparse
import asyncio
import os
import structlog
from taskcraft.core.runtime import AgentRuntime
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.governance.policy import PolicyEngine, ApprovalRequiredPolicy
from taskcraft.llm.client import GeminiClient
from taskcraft.tools.definitions import write_file, read_file, deploy_prod

# Setup logging
structlog.configure(
    processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.dev.ConsoleRenderer()],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

async def run_cli():
    parser = argparse.ArgumentParser(description="TaskCraft: Gemini Agent Runtime")
    subparsers = parser.add_subparsers(dest="command")

    # Command: Run
    run_parser = subparsers.add_parser("run", help="Start a new task")
    run_parser.add_argument("objective", type=str, help="The goal for the agent")

    # Command: Resume
    resume_parser = subparsers.add_parser("resume", help="Resume a task")
    resume_parser.add_argument("task_id", type=str, help="The ID of the task to resume")

    # Command: Approve
    approve_parser = subparsers.add_parser("approve", help="Approve a blocked task")
    approve_parser.add_argument("task_id", type=str, help="The ID of the task to approve")

    args = parser.parse_args()

    # 1. Init Infrastructure
    db_path = "taskcraft_state.db"
    state_manager = SQLiteStateManager(db_path)
    await state_manager.initialize()

    # Define tools map
    tools = {
        "write_file": write_file,
        "read_file": read_file,
        "deploy_prod": deploy_prod
    }

    # Policies
    policy_engine = PolicyEngine(policies=[
        ApprovalRequiredPolicy(sensitive_tools=["deploy_prod"])
    ])

    # Runtime
    runtime = AgentRuntime(state_manager, policy_engine, tools)
    llm_client = GeminiClient() # Expects GOOGLE_API_KEY env var

    if args.command == "run":
        print(f"🚀 Starting task: {args.objective}")
        task = await runtime.create_task(args.objective)
        
        # Start Loop
        await runtime.run_loop(task, llm_client)
        print(f"🏁 Task finished with status: {task.status.name}")
        if task.status.name == "AWAITING_APPROVAL":
            print(f"✋ Task halted. Use 'taskcraft approve {task.task_id}' to continue.")

    elif args.command == "resume":
        print(f"🔄 Resuming task: {args.task_id}")
        task = await runtime.resume_task(args.task_id)
        await runtime.run_loop(task, llm_client)

    elif args.command == "approve":
        print(f"✅ Approving task: {args.task_id}")
        task = await runtime.resume_task(args.task_id)
        if task.status.name != "AWAITING_APPROVAL":
            print(f"Task is in state {task.status.name}, not AWAITING_APPROVAL.")
            return

        # Manually move state forward (In real system, we'd have an 'approve_step' method)
        # Find the pending step
        pending_step = next((s for s in task.steps if s.status == "PENDING_APPROVAL"), None)
        if pending_step:
            print(f"Approving step: {pending_step.name}")
            # Execute it now
            res = await runtime.execute_step(task, pending_step.name, pending_step.input_data)
            print(f"Result: {res}")
            
            # Continue loop
            await runtime.run_loop(task, llm_client)
        else:
            print("No pending steps found.")

if __name__ == "__main__":
    asyncio.run(run_cli())
