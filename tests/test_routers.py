from app.graph.routers import (
    route_after_docs_retrieval,
    route_after_code_retrieval,
    route_after_merge,
)


def test_docs_retrieval_success():
    state = {
        "docs_retrieval_error": ""
    }

    result = route_after_docs_retrieval(
        state
    )

    assert result == "use_docs_results"


def test_docs_retrieval_failure():
    state = {
        "docs_retrieval_error": (
            "RuntimeError: vector store unavailable"
        )
    }

    result = route_after_docs_retrieval(
        state
    )

    assert result == "retrieval_failure"


def test_code_retrieval_success():
    state = {
        "code_retrieval_error": ""
    }

    result = route_after_code_retrieval(
        state
    )

    assert result == "use_code_results"


def test_code_retrieval_failure():
    state = {
        "code_retrieval_error": (
            "RuntimeError: code vector store unavailable"
        )
    }

    result = route_after_code_retrieval(
        state
    )

    assert result == "retrieval_failure"


def test_merge_both_success():
    state = {
        "docs_retrieval_error": "",
        "code_retrieval_error": "",
    }

    result = route_after_merge(
        state
    )

    assert result == "agent"


def test_merge_docs_failure_code_available():
    state = {
        "docs_retrieval_error": (
            "RuntimeError: docs unavailable"
        ),
        "code_retrieval_error": "",
    }

    result = route_after_merge(
        state
    )

    assert result == "agent"


def test_merge_code_failure_docs_available():
    state = {
        "docs_retrieval_error": "",
        "code_retrieval_error": (
            "RuntimeError: code unavailable"
        ),
    }

    result = route_after_merge(
        state
    )

    assert result == "agent"


def test_merge_both_failure():
    state = {
        "docs_retrieval_error": (
            "RuntimeError: docs unavailable"
        ),
        "code_retrieval_error": (
            "RuntimeError: code unavailable"
        ),
    }

    result = route_after_merge(
        state
    )

    assert result == "retrieval_failure"