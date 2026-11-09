from app.graph.schemas import SourceRouteDecision
from app.graph.state import RAGState
from app.models import llm
from app.prompts import SOURCE_ROUTE_PROMPT
from app.rag.retrieval import retrieve_code, retrieve_docs


def source_router_node(
    state: RAGState,
) -> dict:

    question = state.get(
        "standalone_question",
        state["question"],
    )

    # Runtime operational data must come from tools,
    # not from static documentation/code retrieval.
    if _is_runtime_request(
        question
    ):
        return {
            "source_route": "none"
        }

    structured_llm = (
        llm.with_structured_output(
            SourceRouteDecision
        )
    )

    response = structured_llm.invoke(
        [
            (
                "system",
                SOURCE_ROUTE_PROMPT,
            ),
            (
                "user",
                question,
            ),
        ]
    )

    return {
        "source_route": (
            response.source_route
        )
    }

def docs_retrieve_node(state: RAGState) -> dict:
    question = state.get(
        "standalone_question",
        state["question"],
    )

    try:
        results = retrieve_docs(question)

        return {
            "docs_results": results,
            "docs_retrieval_error": "",
        }

    except Exception as error:
        return {
            "docs_results": [],
            "docs_retrieval_error": (
                f"{type(error).__name__}: {error}"
            ),
        }


def code_retrieve_node(state: RAGState) -> dict:
    question = state.get(
        "standalone_question",
        state["question"],
    )

    try:
        results = retrieve_code(question)

        return {
            "code_results": results,
            "code_retrieval_error": "",
        }

    except Exception as error:
        return {
            "code_results": [],
            "code_retrieval_error": (
                f"{type(error).__name__}: {error}"
            ),
        }


def docs_retrieve_both_node(state: RAGState) -> dict:
    return docs_retrieve_node(state)


def code_retrieve_both_node(state: RAGState) -> dict:
    return code_retrieve_node(state)


def use_docs_results_node(state: RAGState) -> dict:
    return {
        "results": state["docs_results"]
    }


def use_code_results_node(state: RAGState) -> dict:
    return {
        "results": state["code_results"]
    }


def merge_results_node(state: RAGState) -> dict:
    docs_results = state.get(
        "docs_results",
        [],
    )

    code_results = state.get(
        "code_results",
        [],
    )

    docs_error = state.get(
        "docs_retrieval_error",
        "",
    )

    code_error = state.get(
        "code_retrieval_error",
        "",
    )

    warning = ""

    if docs_error and not code_error:
        warning = (
            "Document retrieval is temporarily unavailable. "
            "The answer can only use code evidence."
        )

    elif code_error and not docs_error:
        warning = (
            "Code retrieval is temporarily unavailable. "
            "The answer can only use documentation evidence."
        )

    elif docs_error and code_error:
        warning = (
            "Both document and code retrieval are "
            "temporarily unavailable."
        )

    return {
        "results": (
            docs_results
            + code_results
        ),
        "retrieval_warning": warning,
    }

def _is_runtime_request(
    question: str,
) -> bool:

    normalized = question.lower()

    runtime_markers = (
        "right now",
        "currently",
        "current status",
        "recent logs",
        "recent errors",
        "what errors is it showing",
        "how is",
    )

    operational_terms = (
        "health",
        "status",
        "logs",
        "errors",
        "cpu",
        "memory",
        "service",
    )

    has_runtime_marker = any(
        marker in normalized
        for marker in runtime_markers
    )

    has_operational_term = any(
        term in normalized
        for term in operational_terms
    )

    return (
        has_runtime_marker
        and has_operational_term
    )