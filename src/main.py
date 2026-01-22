import asyncio
import structlog
from taskcraft.core.runtime import AgentRuntime
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.governance.policy import PolicyEngine, ApprovalRequiredPolicy
from taskcraft.tools.definitions import write_file, deploy_prod

# Configure basic logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

class MockLLM:
    def __init__(self):
        self.call_count = 0

    async def generate_response(self, history, tools=None):
        self.call_count += 1
        print(f"[MockLLM] generating response {self.call_count}")
        
        # Scenario:
        # 1. Ask to write file (Safe)
        # 2. Ask to deploy (Risky)
        # 3. Done
        
        class MockPart:
            def __init__(self, name, args):
                self.function_call = type('obj', (object,), {'name': name, 'args': args})

        class MockResponse:
            def __init__(self, text, parts=None):
                self.text = text
                self.parts = parts or []

        if self.call_count == 1:
            return MockResponse("I will write a file.", parts=[MockPart("write_file", {"path": "test.txt", "content": "Hello"})])
        elif self.call_count == 2:
            return MockResponse("Now I deploy.", parts=[MockPart("deploy_prod", {"version": "v1"})])
        else:
            return MockResponse("DONE")

async def main():
    print("--- Starting TaskCraft Mock Integration Test ---")
    
    state_manager = SQLiteStateManager("test_integration.db")
    await state_manager.initialize()
    
    policy_engine = PolicyEngine(policies=[
        ApprovalRequiredPolicy(sensitive_tools=["deploy_prod"])
    ])
    
    runtime = AgentRuntime(
        state_manager=state_manager, 
        policy_engine=policy_engine, 
        tools={"write_file": write_file, "deploy_prod": deploy_prod}
    )
    
    mock_llm = MockLLM()
    
    # 2. Create Task
    task = await runtime.create_task("Integration Test Task")
    
    # 3. Run Loop
    await runtime.run_loop(task, mock_llm)
    
    if task.status.name == "AWAITING_APPROVAL":
        print("\n✅ Verification Passed: Runtime halted at deploy_prod")
    else:
        print(f"\n❌ Verification Failed: Task status is {task.status}")

if __name__ == "__main__":
    asyncio.run(main())
