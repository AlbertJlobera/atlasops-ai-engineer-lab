from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from langgraph.prebuilt import ToolNode

from app.graph.nodes import (
    action_blocked_node,
    action_denied_node,
    action_invalid_node,
    action_policy_node,
    action_unauthorized_node,
    answerability_node,
    authorize_action_node,
    build_agent_node,
    code_retrieve_both_node,
    code_retrieve_node,
    docs_retrieve_both_node,
    docs_retrieve_node,
    finalize_answer_node,
    human_approval_node,
    llm_failure_node,
    merge_results_node,
    no_answer_node,
    prepare_code_change_action_node,
    prepare_turn_node,
    propose_code_change_node,
    publish_code_change_node,
    retrieval_failure_node,
    rewrite_question_node,
    source_router_node,
    tool_failure_node,
    use_code_results_node,
    use_docs_results_node,
    validate_action_node,
)

from app.graph.nodes.coding import (
    present_code_change_node,
)

from app.graph.routers import (
    route_after_action_policy,
    route_after_agent,
    route_after_answerability,
    route_after_approval,
    route_after_authorization,
    route_after_code_change_proposal,
    route_after_code_retrieval,
    route_after_docs_retrieval,
    route_after_merge,
    route_after_source_route,
    route_after_tools,
    route_after_validation,
)

from app.graph.state import RAGState


def handle_tool_error(
    error: Exception,
) -> str:
    return (
        "TOOL_ERROR: The requested tool "
        "could not be executed. "
        f"Error type: {type(error).__name__}. "
        "Do not invent the missing "
        "operational information."
    )


def build_workflow(
    tools,
    checkpointer,
):
    graph = StateGraph(
        RAGState
    )

    agent_node = build_agent_node(
        tools
    )

    # ==========================================
    # NODES
    # ==========================================

    # ------------------------------------------
    # Turn preparation
    # ------------------------------------------

    graph.add_node(
        "prepare_turn",
        prepare_turn_node,
    )

    graph.add_node(
        "rewrite_question",
        rewrite_question_node,
    )

    # ------------------------------------------
    # Source routing
    # ------------------------------------------

    graph.add_node(
        "source_router",
        source_router_node,
    )

    # ------------------------------------------
    # Retrieval
    # ------------------------------------------

    graph.add_node(
        "docs_retrieve",
        docs_retrieve_node,
    )

    graph.add_node(
        "docs_retrieve_both",
        docs_retrieve_both_node,
    )

    graph.add_node(
        "code_retrieve",
        code_retrieve_node,
    )

    graph.add_node(
        "code_retrieve_both",
        code_retrieve_both_node,
    )

    graph.add_node(
        "use_docs_results",
        use_docs_results_node,
    )

    graph.add_node(
        "use_code_results",
        use_code_results_node,
    )

    graph.add_node(
        "merge_results",
        merge_results_node,
    )

    # ------------------------------------------
    # Coding agent
    # ------------------------------------------

    graph.add_node(
        "propose_code_change",
        propose_code_change_node,
    )

    graph.add_node(
        "present_code_change",
        present_code_change_node,
    )

    graph.add_node(
        "prepare_code_change_action",
        prepare_code_change_action_node,
    )

    graph.add_node(
        "publish_code_change",
        publish_code_change_node,
    )

    # ------------------------------------------
    # Agent
    # ------------------------------------------

    graph.add_node(
        "agent",
        agent_node,
    )

    # ------------------------------------------
    # Tools
    # ------------------------------------------

    graph.add_node(
        "tools",
        ToolNode(
            tools,
            handle_tool_errors=(
                handle_tool_error
            ),
        ),
    )

    # ------------------------------------------
    # Action validation
    # ------------------------------------------

    graph.add_node(
        "validate_action",
        validate_action_node,
    )

    # ------------------------------------------
    # Authorization
    # ------------------------------------------

    graph.add_node(
        "authorize_action",
        authorize_action_node,
    )

    # ------------------------------------------
    # Policy / guardrails
    # ------------------------------------------

    graph.add_node(
        "action_policy",
        action_policy_node,
    )

    # ------------------------------------------
    # HITL
    # ------------------------------------------

    graph.add_node(
        "human_approval",
        human_approval_node,
    )

    # ------------------------------------------
    # Action failure outcomes
    # ------------------------------------------

    graph.add_node(
        "action_invalid",
        action_invalid_node,
    )

    graph.add_node(
        "action_unauthorized",
        action_unauthorized_node,
    )

    graph.add_node(
        "action_blocked",
        action_blocked_node,
    )

    graph.add_node(
        "action_denied",
        action_denied_node,
    )

    # ------------------------------------------
    # Robustness
    # ------------------------------------------

    graph.add_node(
        "tool_failure",
        tool_failure_node,
    )

    graph.add_node(
        "retrieval_failure",
        retrieval_failure_node,
    )

    graph.add_node(
        "llm_failure",
        llm_failure_node,
    )

    # ------------------------------------------
    # Answer validation
    # ------------------------------------------

    graph.add_node(
        "answerability",
        answerability_node,
    )

    # ------------------------------------------
    # Final output
    # ------------------------------------------

    graph.add_node(
        "finalize_answer",
        finalize_answer_node,
    )

    graph.add_node(
        "no_answer",
        no_answer_node,
    )

    # ==========================================
    # ENTRY FLOW
    # ==========================================

    graph.add_edge(
        START,
        "prepare_turn",
    )

    graph.add_edge(
        "prepare_turn",
        "rewrite_question",
    )

    graph.add_edge(
        "rewrite_question",
        "source_router",
    )

    graph.add_conditional_edges(
        "source_router",
        route_after_source_route,
    )

    # ==========================================
    # DOCUMENT RETRIEVAL
    # ==========================================

    graph.add_conditional_edges(
        "docs_retrieve",
        route_after_docs_retrieval,
    )

    graph.add_edge(
        "use_docs_results",
        "agent",
    )

    # ==========================================
    # CODE RETRIEVAL
    # ==========================================

    graph.add_conditional_edges(
        "code_retrieve",
        route_after_code_retrieval,
    )

    graph.add_edge(
        "use_code_results",
        "agent",
    )

    # ==========================================
    # DOCS + CODE RETRIEVAL
    # ==========================================

    graph.add_edge(
        [
            "docs_retrieve_both",
            "code_retrieve_both",
        ],
        "merge_results",
    )

    graph.add_conditional_edges(
        "merge_results",
        route_after_merge,
    )

    # ==========================================
    # CODING AGENT
    # ==========================================

    graph.add_conditional_edges(
        "propose_code_change",
        route_after_code_change_proposal,
    )

    # Valid proposal becomes a sensitive action.
    graph.add_edge(
        "prepare_code_change_action",
        "validate_action",
    )

    # Invalid proposals are only presented.
    # Nothing is written to GitHub.
    graph.add_edge(
        "present_code_change",
        END,
    )

    # Publication happens only after:
    # validation
    # authorization
    # policy
    # human approval
    graph.add_edge(
        "publish_code_change",
        END,
    )

    # ==========================================
    # AGENT
    # ==========================================

    graph.add_conditional_edges(
        "agent",
        route_after_agent,
    )

    # ==========================================
    # ACTION PIPELINE
    # ==========================================

    graph.add_conditional_edges(
        "validate_action",
        route_after_validation,
    )

    graph.add_conditional_edges(
        "authorize_action",
        route_after_authorization,
    )

    graph.add_conditional_edges(
        "action_policy",
        route_after_action_policy,
    )

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval,
    )

    # ==========================================
    # TOOLS
    # ==========================================

    graph.add_conditional_edges(
        "tools",
        route_after_tools,
    )

    # ==========================================
    # ANSWERABILITY
    # ==========================================

    graph.add_conditional_edges(
        "answerability",
        route_after_answerability,
    )

    # ==========================================
    # TERMINAL NODES
    # ==========================================

    graph.add_edge(
        "finalize_answer",
        END,
    )

    graph.add_edge(
        "no_answer",
        END,
    )

    graph.add_edge(
        "retrieval_failure",
        END,
    )

    graph.add_edge(
        "tool_failure",
        END,
    )

    graph.add_edge(
        "llm_failure",
        END,
    )

    graph.add_edge(
        "action_invalid",
        END,
    )

    graph.add_edge(
        "action_unauthorized",
        END,
    )

    graph.add_edge(
        "action_blocked",
        END,
    )

    graph.add_edge(
        "action_denied",
        END,
    )

    return graph.compile(
        checkpointer=checkpointer
    )