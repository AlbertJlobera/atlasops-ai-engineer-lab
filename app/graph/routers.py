from app.graph.state import RAGState
from app.config import SENSITIVE_TOOLS
from langchain_core.messages import ToolMessage


def route_after_answerability(state: RAGState) -> str:
    if state["answerability"] == "ANSWERABLE":
        return "finalize_answer"

    return "no_answer"

def route_after_source_route(state: RAGState):
    if state["source_route"] == "docs":
        return "docs_retrieve"

    elif state["source_route"] == "code":
        return "code_retrieve"

    elif state["source_route"] == "both":
        return ["docs_retrieve_both", "code_retrieve_both"]

    elif state["source_route"] == "none":
        return "agent"

    raise ValueError(
        f"Invalid source_route: {state['source_route']}"
    )

def route_after_docs_retrieve(state):
    if state["source_route"] == "both":
        return "merge_results"

    return "use_docs_results"

def route_after_code_retrieve(state):
    if state["source_route"] == "both":
        return "merge_results"

    return "use_code_results"

def route_after_agent(state: RAGState):
    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return "answerability"

    for tool_call in last_message.tool_calls:
        if tool_call["name"] in SENSITIVE_TOOLS:
            return "validate_action"

    return "tools"

def route_after_approval(state: RAGState):
    if state["action_approved"]:
        return "tools"

    return "action_denied"

def route_after_action_policy(state: RAGState):

    decision = state["policy_decision"]

    if decision == "blocked":
        return "action_blocked"

    if decision == "requires_approval":
        return "human_approval"

    return "tools"

def route_after_validation(state: RAGState):
    decision = state["validation_decision"]

    if decision == "invalid":
        return "action_invalid"

    return "authorize_action"

def route_after_authorization(state: RAGState):

    if state["authorization_decision"] == "forbidden":
        return "action_unauthorized"

    return "action_policy"

def route_after_tools(state):
    messages = state["messages"]

    # Miramos los ToolMessage generados
    # por la última ejecución de tools.
    for message in reversed(messages):

        if not isinstance(message, ToolMessage):
            break

        if getattr(message, "status", None) == "error":
            return "tool_failure"

    return "agent"

def route_after_docs_retrieval(state):
    if state.get("docs_retrieval_error"):
        return "retrieval_failure"

    return "use_docs_results"

def route_after_code_retrieval(state):
    if state.get(
        "code_retrieval_error"
    ):
        return "retrieval_failure"

    return "use_code_results"

def route_after_merge(state):

    docs_error = state.get(
        "docs_retrieval_error",
        ""
    )

    code_error = state.get(
        "code_retrieval_error",
        ""
    )

    if docs_error and code_error:
        return "retrieval_failure"

    return "agent"