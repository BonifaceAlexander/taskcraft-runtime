from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

class PolicyDecision(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    requires_approval: bool = False

class Policy(ABC):
    """Base class for all governance policies."""
    
    @abstractmethod
    def check(self, action: str, params: dict, context: dict) -> PolicyDecision:
        """Evaluates whether an action is allowed."""
        pass

class MaxActionsPolicy(Policy):
    """Limits the total number of actions per task."""
    def __init__(self, max_actions: int = 10):
        self.max_actions = max_actions

    def check(self, action: str, params: dict, context: dict) -> PolicyDecision:
        current_count = context.get('action_count', 0)
        if current_count >= self.max_actions:
            return PolicyDecision(allowed=False, reason=f"Max actions limit ({self.max_actions}) reached.")
        return PolicyDecision(allowed=True)

class ApprovalRequiredPolicy(Policy):
    """Requires human approval for specific sensitive tools."""
    def __init__(self, sensitive_tools: List[str]):
        self.sensitive_tools = sensitive_tools

    def check(self, action: str, params: dict, context: dict) -> PolicyDecision:
        if action in self.sensitive_tools:
            return PolicyDecision(allowed=False, requires_approval=True, reason=f"Tool '{action}' requires human approval.")
        return PolicyDecision(allowed=True)

class PolicyEngine:
    """Evaluates a list of policies."""
    def __init__(self, policies: List[Policy]):
        self.policies = policies

    def evaluate(self, action: str, params: dict, context: dict) -> PolicyDecision:
        for policy in self.policies:
            decision = policy.check(action, params, context)
            if not decision.allowed:
                return decision
        return PolicyDecision(allowed=True)
