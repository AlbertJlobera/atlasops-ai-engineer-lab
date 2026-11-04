from langgraph import graph
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.graph.nodes import (
    action_blocked_node,
    action_invalid_node,
    action_policy_node,
    action_unauthorized_node,
    answerability_node,
    authorize_action_node,
    llm_failure_node,
    no_answer_node,
    docs_retrieve_node,
    code_retrieve_node,
    merge_results_node,
    retrieval_failure_node,
    source_router_node,
    tool_failure_node,
    use_docs_results_node,
    use_code_results_node,
    finalize_answer_node,
    build_agent_node,
    prepare_turn_node,
    rewrite_question_node,
    human_approval_node,
    action_denied_node,
    validate_action_node,
)
from app.graph.state import RAGState
from app.graph.routers import (
    route_after_action_policy,
    route_after_answerability,
    route_after_authorization,
    route_after_code_retrieval,
    route_after_docs_retrieval,
    route_after_merge,
    route_after_source_route,
    route_after_agent,
    route_after_approval,
    route_after_tools,
    route_after_validation,
)


def handle_tool_error(error: Exception) -> str:
    return (
        "TOOL_ERROR: The requested tool could not be executed. "
        f"Error type: {type(error).__name__}. "
        "Do not invent the missing operational information."
    )



def build_workflow(tools, checkpointer):
    graph = StateGraph(RAGState)

    # El agent se construye con las tools recibidas en runtime
    agent_node = build_agent_node(tools)

    # -------------------------
    # Nodes
    # -------------------------

    graph.add_node("source_router", source_router_node)

    graph.add_node("prepare_turn", prepare_turn_node)

    graph.add_node("docs_retrieve", docs_retrieve_node)
    graph.add_node("docs_retrieve_both", docs_retrieve_node)

    graph.add_node("code_retrieve", code_retrieve_node)
    graph.add_node("code_retrieve_both", code_retrieve_node)

    graph.add_node("use_docs_results", use_docs_results_node)
    graph.add_node("use_code_results", use_code_results_node)
    graph.add_node("merge_results", merge_results_node)

    # HITL
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("action_denied", action_denied_node)

    # Agent
    graph.add_node("agent", agent_node)

    graph.add_node("rewrite_question", rewrite_question_node)
    # Todas las tools, sean locales o MCP
    graph.add_node(
        "tools",
        ToolNode(
        tools,
        handle_tool_errors=handle_tool_error
    )
    )
    # guardrails
    graph.add_node("action_policy", action_policy_node)
    graph.add_node("action_blocked", action_blocked_node)

    # Validation
    graph.add_node("validate_action", validate_action_node)
    graph.add_node("action_invalid", action_invalid_node)

    # Role permitions
    graph.add_node("authorize_action", authorize_action_node)
    graph.add_node("action_unauthorized", action_unauthorized_node)

    # Rebustez
    graph.add_node("tool_failure", tool_failure_node)
    graph.add_node("retrieval_failure", retrieval_failure_node)
    graph.add_node("llm_failure", llm_failure_node)

    graph.add_node("answerability", answerability_node)
    graph.add_node("finalize_answer", finalize_answer_node)
    graph.add_node("no_answer", no_answer_node)

    # -------------------------
    # Edges
    # -------------------------

    # START
    graph.add_edge(
        START,
        "prepare_turn"
    )

    graph.add_edge(
        "prepare_turn",
        "rewrite_question"
    )
    # Source routing:

    graph.add_edge(
        "rewrite_question",
        "source_router"
    )
    # docs / code / both / none
    graph.add_conditional_edges(
        "source_router",
        route_after_source_route
    )

    # -------------------------
    # DOCS
    # -------------------------

    graph.add_conditional_edges(
        "docs_retrieve",
        route_after_docs_retrieval
    )    
    graph.add_edge("use_docs_results", "agent")
    graph.add_edge("retrieval_failure", END)

    # -------------------------
    # CODE
    # -------------------------

    graph.add_conditional_edges(
        "code_retrieve",
        route_after_code_retrieval
    )

    graph.add_edge(
        "use_code_results",
        "agent"
    )

    # -------------------------
    # BOTH
    # -------------------------

    graph.add_edge(
        [
            "docs_retrieve_both",
            "code_retrieve_both"
        ],
        "merge_results"
    )

    graph.add_conditional_edges(
        "merge_results",
        route_after_merge
    )
    # -------------------------
    # AGENTIC TOOL CALLING
    # -------------------------

    graph.add_conditional_edges(
        "agent",
        route_after_agent
    )

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval
    )

    # -------------------------
    # VALIDATION    
    # -------------------------
    graph.add_conditional_edges(
        "validate_action",
        route_after_validation
    )
    graph.add_edge("action_invalid", END)

    # -------------------------
    # ROLE PERMITIONS    
    # -------------------------
    graph.add_conditional_edges(
        "authorize_action",
        route_after_authorization
    )
    graph.add_edge("action_unauthorized", END)

    # Después de ejecutar tools,
    # volvemos al agente
    graph.add_conditional_edges(
        "tools",
        route_after_tools
    )

    graph.add_edge("tool_failure", END)

    # -------------------------
    # GUARDRAILS
    # -------------------------
    graph.add_conditional_edges(
        "action_policy",
        route_after_action_policy
    )

    graph.add_edge("action_blocked", END)

    # -------------------------
    # ANSWERABILITY
    # -------------------------

    graph.add_conditional_edges(
        "answerability",
        route_after_answerability
    )

    # -------------------------
    # FINAL
    # -------------------------

    graph.add_edge(
        "finalize_answer",
        END
    )

    graph.add_edge(
        "no_answer",
        END
    )

    graph.add_edge(
        "action_denied",
        END
    )

    graph.add_edge(
        "llm_failure",
        END
    )

    return graph.compile(
        checkpointer=checkpointer
    )