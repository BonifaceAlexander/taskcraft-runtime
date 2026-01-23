from enum import Enum, auto
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class AgentState(Enum):
    """
    Represents the high-level state of the agent in the runtime.
    
    Transitions:
    IDLE -> PLANNING
    PLANNING -> EXECUTING
    EXECUTING -> PLANNING (Loop) | AWAITING_APPROVAL | COMPLETED | FAILED
    AWAITING_APPROVAL -> EXECUTING (Approved) | FAILED (Rejected)
    FAILED -> PLANNING (Retry) | TERMINATED (Give up)
    """
    IDLE = auto()               # Initial state, waiting for task
    PLANNING = auto()           # Breaking down the user request
    EXECUTING = auto()          # Running tools and actions
    AWAITING_APPROVAL = auto()  # Stopped by governance policy
    COMPLETED = auto()          # Task successfully finished
    FAILED = auto()             # Task failed (after retries)
    TERMINATED = auto()         # Manually stopped

class StepStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()

class LifecycleEvent(BaseModel):
    """
    A record of a state transition or significant event.
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    previous_state: Optional[AgentState]
    new_state: AgentState
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
