from pathlib import PurePosixPath

from langchain_core.messages import ToolMessage
from langgraph.types import interrupt

from app.graph.state import RAGState


def _get_action(
    state: RAGState,
):
    pending_action = state.get(
        "pending_action"
    )

    if pending_action:
        return (
            pending_action["name"],
            pending_action.get(
                "args",
                {},
            ),
            None,
        )

    last_message = (
        state["messages"][-1]
    )

    tool_call = (
        last_message.tool_calls[0]
    )

    return (
        tool_call["name"],
        tool_call["args"],
        tool_call,
    )


def human_approval_node(
    state: RAGState,
) -> dict:

    tool_name, args, tool_call = (
        _get_action(state)
    )

    approval_payload = {
        "type": "tool_approval",
        "tool": tool_name,
        "args": args,
        "message": (
            "Do you approve this action?"
        ),
    }

    if tool_name == "modify_github_code":
        approval_payload.update(
            {
                "diff": state.get(
                    "code_change_diff",
                    "",
                ),
                "summary": (
                    state
                    .get(
                        "code_change_proposal",
                        {},
                    )
                    .get(
                        "summary",
                        "",
                    )
                ),
            }
        )

    approved = interrupt(
        approval_payload
    )

    if approved:
        return {
            "action_approved": True
        }

    if tool_call is not None:
        return {
            "action_approved": False,
            "messages": [
                ToolMessage(
                    content=(
                        "Tool execution denied "
                        "by human reviewer."
                    ),
                    tool_call_id=(
                        tool_call["id"]
                    ),
                    name=tool_name,
                )
            ],
        }

    return {
        "action_approved": False
    }


def validate_action_node(
    state: RAGState,
) -> dict:

    tool_name, args, _ = (
        _get_action(state)
    )

    # ==========================================
    # SERVICE RESTART
    # ==========================================

    if tool_name == "restart_service":

        service_name = args.get(
            "service_name"
        )

        allowed_services = {
            "calculation-service",
            "database-service",
        }

        if service_name not in allowed_services:
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    f"Unknown service: "
                    f"{service_name}"
                ),
            }

    # ==========================================
    # GITHUB CODE MODIFICATION
    # ==========================================

    elif tool_name == "modify_github_code":

        proposal = state.get(
            "code_change_proposal"
        )

        validation = state.get(
            "code_change_validation"
        )

        if not proposal:
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    "Missing code change proposal."
                ),
            }

        if (
            not validation
            or not validation.get("valid")
        ):
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    "The proposed code change "
                    "did not pass validation."
                ),
            }

        file_path = proposal.get(
            "file_path",
            "",
        )

        path = PurePosixPath(
            file_path
        )

        # Prevent absolute paths and traversal
        if (
            not file_path
            or path.is_absolute()
            or ".." in path.parts
        ):
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    "Unsafe repository file path."
                ),
            }

        # Prevent changes to GitHub Actions workflows
        if file_path.startswith(
            ".github/workflows/"
        ):
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    "Modifying GitHub Actions workflows "
                    "is prohibited by policy."
                ),
            }

        # GitHub optimistic concurrency protection
        if not proposal.get(
            "original_sha"
        ):
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    "Missing original GitHub SHA."
                ),
            }

    return {
        "validation_decision": "valid",
        "validation_reason": "",
    }


def authorize_action_node(
    state: RAGState,
) -> dict:

    tool_name, _, _ = (
        _get_action(state)
    )

    user_role = state.get(
        "user_role",
        "viewer",
    )

    sensitive_actions = {
        "restart_service",
        "modify_github_code",
    }

    if tool_name in sensitive_actions:

        if user_role not in {
            "operator",
            "admin",
        }:
            return {
                "authorization_decision": (
                    "forbidden"
                ),
                "authorization_reason": (
                    f"Role '{user_role}' is not "
                    f"allowed to execute "
                    f"'{tool_name}'."
                ),
            }

    return {
        "authorization_decision": "allowed",
        "authorization_reason": "",
    }


def action_policy_node(
    state: RAGState,
) -> dict:

    tool_name, args, _ = (
        _get_action(state)
    )

    # ==========================================
    # SERVICE RESTART POLICY
    # ==========================================

    if tool_name == "restart_service":

        service_name = args.get(
            "service_name"
        )

        if service_name == "database-service":
            return {
                "policy_decision": "blocked",
                "policy_reason": (
                    "Restarting database-service "
                    "is prohibited by policy."
                ),
            }

        return {
            "policy_decision": (
                "requires_approval"
            ),
            "policy_reason": (
                "Restarting a service requires "
                "human approval."
            ),
        }

    # ==========================================
    # GITHUB CODE CHANGE POLICY
    # ==========================================

    if tool_name == "modify_github_code":
        return {
            "policy_decision": (
                "requires_approval"
            ),
            "policy_reason": (
                "Repository modifications require "
                "human approval."
            ),
        }

    return {
        "policy_decision": "allowed",
        "policy_reason": (
            "Action is allowed."
        ),
    }


def action_denied_node(
    state: RAGState,
) -> dict:

    return {
        "answer": (
            "The requested action was not executed "
            "because human approval was denied."
        ),
        "sources": [],
    }


def action_blocked_node(
    state: RAGState,
) -> dict:

    reason = state.get(
        "policy_reason",
        "The action was blocked by policy.",
    )

    return {
        "answer": reason,
        "sources": [],
    }


def action_invalid_node(
    state: RAGState,
) -> dict:

    reason = state.get(
        "validation_reason",
        "The requested action is invalid.",
    )

    return {
        "answer": reason,
        "sources": [],
    }


def action_unauthorized_node(
    state: RAGState,
) -> dict:

    reason = state.get(
        "authorization_reason",
        (
            "You are not authorized "
            "to perform this action."
        ),
    )

    return {
        "answer": reason,
        "sources": [],
    }