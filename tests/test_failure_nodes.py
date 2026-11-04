from langchain_core.messages import ToolMessage

from app.graph.nodes import (
    retrieval_failure_node,
    tool_failure_node,
    llm_failure_node,
)


# =========================================================
# RETRIEVAL FAILURE
# =========================================================

def test_docs_retrieval_failure_response():
    state = {
        "docs_retrieval_error": (
            "RuntimeError: docs unavailable"
        ),
        "code_retrieval_error": "",
    }

    result = retrieval_failure_node(state)

    assert (
        "document knowledge"
        in result["answer"]
    )

    assert (
        "temporarily unavailable"
        in result["answer"]
    )

    assert result["sources"] == []


def test_code_retrieval_failure_response():
    state = {
        "docs_retrieval_error": "",
        "code_retrieval_error": (
            "RuntimeError: code unavailable"
        ),
    }

    result = retrieval_failure_node(state)

    assert (
        "code knowledge"
        in result["answer"]
    )

    assert (
        "temporarily unavailable"
        in result["answer"]
    )

    assert result["sources"] == []


def test_both_retrieval_failure_response():
    state = {
        "docs_retrieval_error": (
            "RuntimeError: docs unavailable"
        ),
        "code_retrieval_error": (
            "RuntimeError: code unavailable"
        ),
    }

    result = retrieval_failure_node(state)

    assert (
        "document and code knowledge"
        in result["answer"]
    )

    assert (
        "temporarily unavailable"
        in result["answer"]
    )

    assert result["sources"] == []


# =========================================================
# TOOL FAILURE
# =========================================================

def test_tool_failure_response():

    tool_message = ToolMessage(
        content=(
            "Error executing tool "
            "get_service_health"
        ),
        tool_call_id="test-call-1",
        name="get_service_health",
        status="error",
    )

    state = {
        "messages": [
            tool_message
        ]
    }

    result = tool_failure_node(state)

    assert (
        "get_service_health"
        in result["answer"]
    )

    assert (
        "temporarily unavailable"
        in result["answer"]
    )

    assert result["sources"] == []


def test_multiple_tool_failures_response():

    health_error = ToolMessage(
        content="Health tool failed",
        tool_call_id="test-call-1",
        name="get_service_health",
        status="error",
    )

    logs_error = ToolMessage(
        content="Logs tool failed",
        tool_call_id="test-call-2",
        name="get_service_logs",
        status="error",
    )

    state = {
        "messages": [
            health_error,
            logs_error,
        ]
    }

    result = tool_failure_node(state)

    assert (
        "get_service_health"
        in result["answer"]
    )

    assert (
        "get_service_logs"
        in result["answer"]
    )

    assert result["sources"] == []


# =========================================================
# LLM FAILURE
# =========================================================

def test_llm_failure_response():

    state = {
        "llm_error": (
            "RuntimeError: "
            "OpenAI unavailable"
        )
    }

    result = llm_failure_node(state)

    assert (
        "AI service is temporarily unavailable"
        in result["answer"]
    )

    assert result["sources"] == []