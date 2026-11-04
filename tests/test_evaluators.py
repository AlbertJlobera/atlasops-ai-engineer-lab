from langchain_core.messages import AIMessage, ToolMessage

from evaluation.evaluators import (
    get_called_tools,
    has_tool_error,
    has_empty_results,
    has_retrieval_error,
    has_code_retrieval_error,
    has_retrieval_warning,
    has_docs_and_code_failure,
    answer_contains_warning,
    answer_mentions_both_retrieval_failures,
    has_llm_error,
)


def test_get_called_tools():
    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_service_health",
                "args": {
                    "service_name": "calculation-service"
                },
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )

    result = get_called_tools([message])

    assert result == [
        "get_service_health"
    ]


def test_has_tool_error_true():
    message = ToolMessage(
        content="Tool failed",
        tool_call_id="call-1",
        name="get_service_health",
        status="error",
    )

    assert has_tool_error(
        [message]
    ) is True


def test_has_tool_error_false():
    message = ToolMessage(
        content="Tool succeeded",
        tool_call_id="call-1",
        name="get_service_health",
        status="success",
    )

    assert has_tool_error(
        [message]
    ) is False


def test_has_empty_results():
    assert has_empty_results([]) is True
    assert has_empty_results([1]) is False


def test_has_docs_retrieval_error():
    result = {
        "docs_retrieval_error": (
            "RuntimeError"
        )
    }

    assert has_retrieval_error(
        result
    ) is True


def test_has_code_retrieval_error():
    result = {
        "code_retrieval_error": (
            "RuntimeError"
        )
    }

    assert has_code_retrieval_error(
        result
    ) is True


def test_has_retrieval_warning():
    result = {
        "retrieval_warning": (
            "Code retrieval unavailable."
        )
    }

    assert has_retrieval_warning(
        result
    ) is True


def test_has_docs_and_code_failure():
    result = {
        "docs_retrieval_error": (
            "docs failed"
        ),
        "code_retrieval_error": (
            "code failed"
        ),
    }

    assert has_docs_and_code_failure(
        result
    ) is True


def test_warning_is_in_answer():
    warning = (
        "Code retrieval is temporarily unavailable."
    )

    result = {
        "retrieval_warning": warning,
        "answer": (
            "Partial response.\n\n"
            f"Warning: {warning}"
        ),
    }

    assert answer_contains_warning(
        result
    ) is True


def test_answer_mentions_both_failures():
    result = {
        "answer": (
            "I couldn't retrieve the requested "
            "document and code knowledge."
        )
    }

    assert (
        answer_mentions_both_retrieval_failures(
            result
        )
        is True
    )


def test_has_llm_error():
    result = {
        "llm_error": (
            "RuntimeError: OpenAI unavailable"
        )
    }

    assert has_llm_error(
        result
    ) is True