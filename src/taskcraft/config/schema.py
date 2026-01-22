from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    name: Optional[str] = None # Name of built-in tool
    module: Optional[str] = None # Path to python module to import
    
class PolicyConfig(BaseModel):
    max_actions: Optional[int] = None
    approval_required: List[str] = Field(default_factory=list)

class AgentConfig(BaseModel):
    name: str
    description: str
    objective: str
    tools: List[ToolConfig] = Field(default_factory=list)
    policies: PolicyConfig = Field(default_factory=PolicyConfig)
