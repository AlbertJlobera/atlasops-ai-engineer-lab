from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)

from app.graph.state import RAGState
from app.rag.answerability import (
    judge_answerability,
)


def answerability_node(
    state: RAGState,
) -> dict:

    question = state["question"]

    results = state.get(
        "results",
        [],
    )

    messages = state.get(
        "messages",
        [],
    )

    last_human_index = 0

    for i in range(
        len(messages) - 1,
        -1,
        -1,
    ):
        if isinstance(
            messages[i],
            HumanMessage,
        ):
            last_human_index = i
            break

    current_turn_messages = (
        messages[last_human_index:]
    )

    tool_messages = [
        message
        for message in current_turn_messages
        if isinstance(
            message,
            ToolMessage,
        )
    ]

    answerability = (
        judge_answerability(
            question,
            results,
            tool_messages,
        )
    )

    return {
        "answerability": answerability
    }


def no_answer_node(
    state: RAGState,
) -> dict:

    return {
        "answer": (
            "I'm sorry, but I cannot provide "
            "an answer to your question based "
            "on the available information."
        ),
        "sources": [],
    }