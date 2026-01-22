from abc import ABC, abstractmethod
from typing import Optional, List
import json
import aiosqlite
from pathlib import Path
from taskcraft.state.models import Task
from taskcraft.core.lifecycle import AgentState

class StateManager(ABC):
    """Abstract base class for state persistence."""
    
    @abstractmethod
    async def save_task(self, task: Task) -> None:
        """Saves or updates a task."""
        pass

    @abstractmethod
    async def load_task(self, task_id: str) -> Optional[Task]:
        """Loads a task by ID."""
        pass

    @abstractmethod
    async def list_tasks(self, status: Optional[AgentState] = None) -> List[Task]:
        """Lists tasks, optionally filtering by status."""
        pass

class SQLiteStateManager(StateManager):
    """SQLite implementation of StateManager."""
    
    def __init__(self, db_path: str = "taskcraft_state.db"):
        self.db_path = db_path

    async def initialize(self):
        """Creates the necessary tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT,
                    data JSON,
                    updated_at TIMESTAMP
                )
            """)
            await db.commit()

    async def save_task(self, task: Task) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO tasks (task_id, status, data, updated_at) VALUES (?, ?, ?, ?)",
                (task.task_id, task.status.value if hasattr(task.status, 'value') else task.status, task.model_dump_json(), task.updated_at)
            )
            await db.commit()

    async def load_task(self, task_id: str) -> Optional[Task]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT data FROM tasks WHERE task_id = ?", (task_id,))
            row = await cursor.fetchone()
            if row:
                return Task.model_validate_json(row[0])
            return None

    async def list_tasks(self, status: Optional[AgentState] = None) -> List[Task]:
        query = "SELECT data FROM tasks"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status.value if hasattr(status, 'value') else status)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, tuple(params))
            rows = await cursor.fetchall()
            return [Task.model_validate_json(row[0]) for row in rows]
