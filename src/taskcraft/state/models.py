from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from taskcraft.core.lifecycle import AgentState

def generate_id():
    return str(uuid.uuid4())

class Step(BaseModel):
    """Represents a single atomic action or thought within a task."""
    step_id: str = Field(default_factory=generate_id)
    task_id: str
    index: int
    name: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Task(BaseModel):
    """Represents a high-level user request or task."""
    task_id: str = Field(default_factory=generate_id)
    description: str
    status: AgentState = AgentState.IDLE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Checkpoint data
    steps: List[Step] = Field(default_factory=list)
    current_step_index: int = 0
    history: List[str] = Field(default_factory=list) # Simple log of events
