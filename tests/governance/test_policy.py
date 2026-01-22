import pytest
from taskcraft.governance.policy import PolicyEngine, MaxActionsPolicy, ApprovalRequiredPolicy

def test_max_actions_policy():
    policy = MaxActionsPolicy(max_actions=2)
    context_ok = {'action_count': 1}
    context_limit = {'action_count': 2}
    
    assert policy.check("any", {}, context_ok).allowed is True
    assert policy.check("any", {}, context_limit).allowed is False

def test_approval_policy():
    policy = ApprovalRequiredPolicy(sensitive_tools=["nuke_prod"])
    
    # Safe tool
    decision = policy.check("ls", {}, {})
    assert decision.allowed is True
    
    # Risky tool
    decision = policy.check("nuke_prod", {}, {})
    assert decision.allowed is False
    assert decision.requires_approval is True

def test_policy_engine_aggregation():
    engine = PolicyEngine(policies=[
        MaxActionsPolicy(max_actions=5),
        ApprovalRequiredPolicy(sensitive_tools=["deploy"])
    ])
    
    # 1. Allowed
    res = engine.evaluate("read", {}, {'action_count': 0})
    assert res.allowed is True
    
    # 2. Blocked by Approval
    res = engine.evaluate("deploy", {}, {'action_count': 0})
    assert res.allowed is False
    assert res.requires_approval is True
    
    # 3. Blocked by Limit
    res = engine.evaluate("read", {}, {'action_count': 5})
    assert res.allowed is False
    assert "limit" in res.reason
