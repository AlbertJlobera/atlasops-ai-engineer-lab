from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from app.graph.state import RAGState


def route_after_agent(
    state: RAGState,
) -> str:

    if state.get("llm_error"):
        return "llm_failure"

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return "llm_failure"

    last_message = messages[-1]

    if not isinstance(
        last_message,
        AIMessage,
    ):
        return "llm_failure"

    if not last_message.tool_calls:
        return "answerability"

    for tool_call in (
        last_message.tool_calls
    ):
        if (
            tool_call["name"]
            == "restart_service"
        ):
            return "validate_action"

    return "tools"


def route_after_validation(
    state: RAGState,
) -> str:

    decision = state[
        "validation_decision"
    ]

    if decision == "invalid":
        return "action_invalid"

    return "authorize_action"


def route_after_authorization(
    state: RAGState,
) -> str:

    decision = state[
        "authorization_decision"
    ]

    if decision == "forbidden":
        return "action_unauthorized"

    return "action_policy"


def route_after_action_policy(
    state: RAGState,
) -> str:

    decision = state[
        "policy_decision"
    ]

    if decision == "blocked":
        return "action_blocked"

    if decision == "requires_approval":
        return "human_approval"

    return "tools"


def route_after_approval(
    state: RAGState,
) -> str:

    if not state["action_approved"]:
        return "action_denied"

    pending_action = state.get(
        "pending_action"
    )

    if (
        pending_action
        and pending_action["name"]
        == "modify_github_code"
    ):
        return "publish_code_change"

    return "tools"


def route_after_tools(
    state: RAGState,
) -> str:

    messages = state[
        "messages"
    ]

    for message in reversed(
        messages
    ):
        if not isinstance(
            message,
            ToolMessage,
        ):
            break

        if (
            getattr(
                message,
                "status",
                None,
            )
            == "error"
        ):
            return "tool_failure"

    return "agent"

def route_after_code_change_proposal(
    state: RAGState,
) -> str:

    validation = state.get(
        "code_change_validation"
    )

    if (
        not validation
        or not validation.get("valid")
    ):
        return "present_code_change"

    return "prepare_code_change_action"