from typing import TypedDict, Any


class RAGState(TypedDict, total=False):
    question: str
    results: list[Any]
    answerability: str
    answer: str
    sources: list[dict]