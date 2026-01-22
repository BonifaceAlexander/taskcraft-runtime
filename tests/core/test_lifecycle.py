import pytest
import asyncio
from taskcraft.core.runtime import AgentRuntime
from taskcraft.core.lifecycle import AgentState
from taskcraft.state.models import Task

@pytest.mark.asyncio
async def test_create_task(memory_db, empty_policy_engine):
    runtime = AgentRuntime(memory_db, empty_policy_engine, tools={})
    
    task = await runtime.create_task("Test Objective")
    
    assert task.description == "Test Objective"
    assert task.status == AgentState.PLANNING
    assert task.task_id is not None

@pytest.mark.asyncio
async def test_execute_safe_step(memory_db, empty_policy_engine):
    async def mock_tool(arg: str):
        return f"echo {arg}"
        
    runtime = AgentRuntime(memory_db, empty_policy_engine, tools={"echo": mock_tool})
    task = await runtime.create_task("Test")
    
    # Manually trigger a step
    result = await runtime.execute_step(task, "echo", {"arg": "hello"})
    
    assert result["status"] == "SUCCESS"
    assert "echo hello" in result["output"]
    assert len(task.steps) == 1
    assert task.steps[0].status == "COMPLETED"
    assert task.status == AgentState.EXECUTING
