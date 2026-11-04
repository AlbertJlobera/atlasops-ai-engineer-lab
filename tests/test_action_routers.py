from app.graph.routers import (
    route_after_validation,
    route_after_authorization,
    route_after_action_policy,
)


# =========================================================
# VALIDATION
# =========================================================

def test_validation_valid():
    state = {
        "validation_decision": "valid"
    }

    result = route_after_validation(state)

    assert result == "authorize_action"


def test_validation_invalid():
    state = {
        "validation_decision": "invalid"
    }

    result = route_after_validation(state)

    assert result == "action_invalid"


# =========================================================
# AUTHORIZATION
# =========================================================

def test_authorization_allowed():
    state = {
        "authorization_decision": "allowed"
    }

    result = route_after_authorization(state)

    assert result == "action_policy"


def test_authorization_forbidden():
    state = {
        "authorization_decision": "forbidden"
    }

    result = route_after_authorization(state)

    assert result == "action_unauthorized"


# =========================================================
# POLICY
# =========================================================

def test_policy_allowed():
    state = {
        "policy_decision": "allowed"
    }

    result = route_after_action_policy(state)

    assert result == "tools"


def test_policy_requires_approval():
    state = {
        "policy_decision": "requires_approval"
    }

    result = route_after_action_policy(state)

    assert result == "human_approval"


def test_policy_blocked():
    state = {
        "policy_decision": "blocked"
    }

    result = route_after_action_policy(state)

    assert result == "action_blocked"