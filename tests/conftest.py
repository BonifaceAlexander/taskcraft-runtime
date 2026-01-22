import pytest
import asyncio
from typing import Generator
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.core.runtime import AgentRuntime
from taskcraft.governance.policy import PolicyEngine

@pytest.fixture
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def memory_db(tmp_path):
    """Returns a SQLite state manager backed by a temp file."""
    # Use a temp file because SQLiteStateManager opens a new connection per call.
    # :memory: DBs are wiped when connection closes.
    db_path = tmp_path / "test_state.db"
    db = SQLiteStateManager(str(db_path))
    await db.initialize()
    return db

@pytest.fixture
def empty_policy_engine():
    return PolicyEngine(policies=[])
