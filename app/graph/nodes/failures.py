from langchain_core.messages import ToolMessage

from app.graph.state import RAGState


def llm_failure_node(
    state: RAGState,
) -> dict:
    return {
        "answer": (
            "I couldn't process the request because "
            "the AI service is temporarily unavailable. "
            "Please try again later."
        ),
        "sources": [],
    }


def tool_failure_node(
    state: RAGState,
) -> dict:

    failed_tools = []

    for message in reversed(
        state["messages"]
    ):
        if not isinstance(
            message,
            ToolMessage,
        ):
            break

        if (
            getattr(
                message,
                "status",
                None,
            )
            == "error"
        ):
            failed_tools.append(
                message.name
                or "unknown_tool"
            )

    tool_names = ", ".join(
        reversed(failed_tools)
    )

    return {
        "answer": (
            "I couldn't retrieve the requested "
            "operational information because "
            "the following tool failed: "
            f"{tool_names}. "
            "The information is temporarily "
            "unavailable."
        ),
        "sources": [],
    }


def retrieval_failure_node(
    state: RAGState,
) -> dict:

    docs_error = state.get(
        "docs_retrieval_error",
        "",
    )

    code_error = state.get(
        "code_retrieval_error",
        "",
    )

    if docs_error and code_error:
        source = "document and code"

    elif docs_error:
        source = "document"

    elif code_error:
        source = "code"

    else:
        source = "knowledge"

    return {
        "answer": (
            f"I couldn't retrieve the requested "
            f"{source} knowledge because the "
            "retrieval service is temporarily "
            "unavailable."
        ),
        "sources": [],
    }