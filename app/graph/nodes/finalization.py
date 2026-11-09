from app.graph.state import RAGState
from app.rag.sources import build_sources


def finalize_answer_node(
    state: RAGState,
) -> dict:

    answer = (
        state["messages"][-1].content
    )

    retrieval_warning = state.get(
        "retrieval_warning",
        "",
    )

    if retrieval_warning:
        answer = (
            f"{answer}\n\n"
            f"Warning: {retrieval_warning}"
        )

    return {
        "answer": answer,
        "sources": build_sources(
            state.get(
                "results",
                [],
            )
        ),
    }