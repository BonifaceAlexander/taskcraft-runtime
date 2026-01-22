import argparse
import asyncio
import os
import structlog
import json
from taskcraft.core.runtime import AgentRuntime
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.governance.policy import PolicyEngine, ApprovalRequiredPolicy, MaxActionsPolicy
from taskcraft.planner.gemini import GeminiPlanner
from taskcraft.tools.definitions import write_file, read_file, deploy_prod
from taskcraft.config.loader import load_config, load_tools
from taskcraft.observability.logger import configure_logger, get_logger

# Executor Impls
from taskcraft.executor.local import LocalExecutor

# Setup logging
configure_logger()
logger = get_logger()

async def run_cli():
    parser = argparse.ArgumentParser(description="TaskCraft: Gemini Agent Runtime")
    
    # Global Flags
    parser.add_argument("--backend", choices=["sqlite", "postgres"], default="sqlite", help="State backend")
    
    subparsers = parser.add_subparsers(dest="command")

    # Command: Run
    run_parser = subparsers.add_parser("run", help="Start a new task")
    run_parser.add_argument("--objective", "-o", type=str, help="The goal for the agent")
    run_parser.add_argument("--file", "-f", type=str, help="Path to agent configuration file (YAML)")
    run_parser.add_argument("--executor", choices=["local", "docker"], default="local", help="Execution environment")
    run_parser.add_argument("--planner", choices=["gemini", "tot"], default="gemini", help="Reasoning engine")

    # Command: Resume
    resume_parser = subparsers.add_parser("resume", help="Resume a task")
    resume_parser.add_argument("task_id", type=str, help="The ID of the task to resume")

    # Command: Approve
    approve_parser = subparsers.add_parser("approve", help="Approve a blocked task")
    approve_parser.add_argument("task_id", type=str, help="The ID of the task to approve")

    # Command: Status
    status_parser = subparsers.add_parser("status", help="Get status of a task")
    status_parser.add_argument("task_id", type=str, help="The ID of the task")

    # Command: Logs
    logs_parser = subparsers.add_parser("logs", help="Get detailed logs/trace of a task")
    logs_parser.add_argument("task_id", type=str, help="The ID of the task")


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # 1. Init Infrastructure (Factory)
    state_manager = None
    if args.backend == "sqlite":
        db_path = os.getenv("SQLITE_DB_PATH", "taskcraft_state.db")
        state_manager = SQLiteStateManager(db_path)
    elif args.backend == "postgres":
        from taskcraft.state.postgres import PostgresStateManager
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ Error: DATABASE_URL must be set for postgres backend.")
            return
        state_manager = PostgresStateManager(db_url)
    
    await state_manager.initialize()

    # 2. Command Handling
    if args.command == "run":
        # Load Config & Tools
        tools = {}
        policies = []
        config_name = "Agent"
        
        if args.file:
            print(f"📂 Loading configuration from {args.file}...")
            try:
                config = load_config(args.file)
                tools = load_tools(config)
                if config.policies.max_actions:
                    policies.append(MaxActionsPolicy(max_actions=config.policies.max_actions))
                if config.policies.approval_required:
                    policies.append(ApprovalRequiredPolicy(sensitive_tools=config.policies.approval_required))
                task_objective = args.objective if args.objective else config.objective
                config_name = config.name
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                return
        else:
            if not args.objective:
                print("❌ Error: --objective is required.")
                return
            tools = {"write_file": write_file, "read_file": read_file, "deploy_prod": deploy_prod}
            policies = [ApprovalRequiredPolicy(["deploy_prod"]), MaxActionsPolicy(10)]
            task_objective = args.objective

        policy_engine = PolicyEngine(policies=policies)

        # Factory: Executor
        executor = None
        if args.executor == "local":
             executor = LocalExecutor(tools)
        elif args.executor == "docker":
             from taskcraft.executor.docker import DockerExecutor
             # In v1, DockerExecutor behaves differently (serialization gap).
             # implementing basic fallback or direct usage for now.
             print("🐳 Using Docker Executor (Sandbox Mode)")
             executor = DockerExecutor() 
             # Warning: We are passing tools to DockerExecutor but v1 implementation 
             # needs better protocol. For now, it runs 'run_shell'.

        # Factory: Planner
        planner = None
        if args.planner == "gemini":
            planner = GeminiPlanner()
        elif args.planner == "tot":
            from taskcraft.planner.tot import TreeOfThoughtsPlanner
            planner = TreeOfThoughtsPlanner()

        # Runtime
        print(f"🤖 Agent: {config_name} | Backend: {args.backend} | Executor: {args.executor}")
        runtime = AgentRuntime(state_manager, policy_engine, executor)

        print(f"🚀 Starting task: {task_objective}")
        task = await runtime.create_task(task_objective)
        
        await runtime.run_loop(task, planner)
        print(f"🏁 Task finished with status: {task.status.name}")
        if task.status.name == "AWAITING_APPROVAL":
            print(f"✋ Task halted. Use 'taskcraft approve {task.task_id}' to continue.")

    elif args.command == "resume" or args.command == "approve":
        # Simplified Resume Logic (Recreating runtime components)
        # Note: In a real distributed system, the worker process would self-assemble based on config.
        # Here we default to LocalExecutor + GeminiPlanner for simple resumption.
        
        print(f"Runnning command: {args.command} on {args.task_id}")
        
        # Tools Hack for Demo (Incident Reporter)
        from examples.incident_tools import send_report, fetch_incidents
        tools = {"send_report": send_report, "fetch_incidents": fetch_incidents}
        
        executor = LocalExecutor(tools)
        planner = GeminiPlanner()
        policy_engine = PolicyEngine([]) # Relaxed policy or reloaded

        runtime = AgentRuntime(state_manager, policy_engine, executor)
        
        if args.command == "resume":
             task = await runtime.resume_task(args.task_id)
             if task.status.name == "COMPLETED":
                 print("Task already completed")
             else:
                 await runtime.run_loop(task, planner)
                 
        elif args.command == "approve":
             task = await runtime.resume_task(args.task_id)
             if task.status.name != "AWAITING_APPROVAL":
                  print(f"Task is {task.status.name}, not AWAITING_APPROVAL")
                  return
                  
             pending_step = next((s for s in task.steps if s.status == "PENDING_APPROVAL"), None)
             if pending_step:
                 print(f"Approving step: {pending_step.name}")
                 await runtime.execute_step(task, pending_step.name, pending_step.input_data)
                 # Reload & Continue
                 task.status = "EXECUTING"
                 await runtime.run_loop(task, planner)
             else:
                 print("No pending steps.")

    elif args.command == "status":
        task = await state_manager.load_task(args.task_id)
        if not task:
            print("Task not found.")
            return
        print(f"Task: {task.task_id}")
        print(f"Status: {task.status.name}")
        print(f"Steps: {len(task.steps)}")
        print(f"Created: {task.created_at}")

    elif args.command == "logs":
        task = await state_manager.load_task(args.task_id)
        if not task:
            print("Task not found.")
            return
        print(json.dumps({
            "id": task.task_id,
            "status": task.status.name,
            "steps": [s.model_dump() for s in task.steps]
        }, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(run_cli())
