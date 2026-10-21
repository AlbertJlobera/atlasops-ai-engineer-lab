

from app.graph.state import RAGState


def route_after_answerability(state: RAGState) -> str:
    if state["answerability"] == "ANSWERABLE":
        return "generate"

    return "no_answer"