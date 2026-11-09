from app.graph.state import RAGState


def route_after_source_route(
    state: RAGState,
):
    route = state["source_route"]

    if route == "docs":
        return "docs_retrieve"

    if route == "code":
        return "code_retrieve"

    if route == "both":
        return [
            "docs_retrieve_both",
            "code_retrieve_both",
        ]

    if route == "code_change":
        return "propose_code_change"

    if route == "none":
        return "agent"

    raise ValueError(
        f"Invalid source_route: {route}"
    )


def route_after_docs_retrieval(
    state: RAGState,
) -> str:

    if state.get(
        "docs_retrieval_error"
    ):
        return "retrieval_failure"

    return "use_docs_results"


def route_after_code_retrieval(
    state: RAGState,
) -> str:

    if state.get(
        "code_retrieval_error"
    ):
        return "retrieval_failure"

    return "use_code_results"


def route_after_merge(
    state: RAGState,
) -> str:

    docs_error = state.get(
        "docs_retrieval_error",
        "",
    )

    code_error = state.get(
        "code_retrieval_error",
        "",
    )

    if docs_error and code_error:
        return "retrieval_failure"

    return "agent"


def route_after_answerability(
    state: RAGState,
) -> str:

    if (
        state["answerability"]
        == "ANSWERABLE"
    ):
        return "finalize_answer"

    return "no_answer"