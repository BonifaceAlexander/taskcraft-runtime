from typing import List, Optional
from datetime import datetime
import json
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text

from taskcraft.state.persistence import StateManager
from taskcraft.state.models import Task, Step
from taskcraft.core.lifecycle import AgentState

logger = structlog.get_logger()
Base = declarative_base()

# --- SQL Models ---

class TaskModel(Base):
    __tablename__ = 'tasks'
    
    task_id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # steps relationship would be handled by query

class StepModel(Base):
    __tablename__ = 'steps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey('tasks.task_id'), nullable=False)
    index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True) # JSONB in Postgres
    output_data = Column(JSON, nullable=True)
    status = Column(String, nullable=False)
    error = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

# --- State Manager ---

class PostgresStateManager(StateManager):
    def __init__(self, connection_string: str):
        """
        Args:
            connection_string: e.g. "postgresql+asyncpg://user:pass@localhost/dbname"
        """
        self.engine = create_async_engine(connection_string, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self):
        """Creates tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Postgres initialized")

    async def save_task(self, task: Task):
        """Upserts a task and its steps."""
        async with self.async_session() as session:
            async with session.begin():
                # 1. Upsert Task
                existing_task = await session.get(TaskModel, task.task_id)
                if not existing_task:
                    existing_task = TaskModel(task_id=task.task_id)
                    session.add(existing_task)
                
                existing_task.description = task.description
                existing_task.status = task.status.name
                existing_task.updated_at = task.updated_at

                # 2. Sync Steps
                # For simplicity in this implementation, we can check existing steps and insert new ones
                # knowing that 'index' is unique per task.
                # A full sync might be more complex, but this is append-only mostly.
                
                # In a real high-throughput system, we'd batch insert only new steps.
                # Here we loop for simplicity / correctness of updates.
                from sqlalchemy import select
                
                for step_obj in task.steps:
                     # Check if step exists
                     result = await session.execute(
                         select(StepModel).where(StepModel.task_id == task.task_id, StepModel.index == step_obj.index)
                     )
                     db_step = result.scalars().first()
                     
                     if not db_step:
                         db_step = StepModel(
                             task_id=task.task_id,
                             index=step_obj.index
                         )
                         session.add(db_step)
                    
                     # Update fields
                     db_step.name = step_obj.name
                     db_step.input_data = step_obj.input_data
                     db_step.output_data = step_obj.output_data
                     db_step.status = step_obj.status
                     db_step.error = step_obj.error
                     db_step.start_time = step_obj.start_time
                     db_step.end_time = step_obj.end_time

    async def load_task(self, task_id: str) -> Optional[Task]:
        async with self.async_session() as session:
            # Load Task
            result = await session.execute(
                from sqlalchemy import select
                select(TaskModel).where(TaskModel.task_id == task_id)
            )
            db_task = result.scalars().first()
            
            if not db_task:
                return None
            
            # Load Steps
            result_steps = await session.execute(
                select(StepModel).where(StepModel.task_id == task_id).order_by(StepModel.index)
            )
            db_steps = result_steps.scalars().all()
            
            # Reconstruct Domain Objects
            steps_list = []
            for s in db_steps:
                steps_list.append(Step(
                    task_id=s.task_id,
                    index=s.index,
                    name=s.name,
                    input_data=s.input_data or {},
                    output_data=s.output_data,
                    status=s.status,
                    error=s.error,
                    start_time=s.start_time,
                    end_time=s.end_time
                ))
            
            return Task(
                task_id=db_task.task_id,
                description=db_task.description,
                status=AgentState[db_task.status],
                created_at=db_task.created_at,
                updated_at=db_task.updated_at,
                steps=steps_list
            )

    async def list_tasks(self) -> List[Task]:
        # Implementation omitted for brevity logic similar to load_task but loop
        return [] 
