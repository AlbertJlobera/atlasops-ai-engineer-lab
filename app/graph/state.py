from typing import TypedDict, Any, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class RAGState(TypedDict, total=False):
    question: str
    standalone_question: str

    messages: Annotated[list[AnyMessage], add_messages]

    # RAG routing
    source_route: str
    docs_results: list[Any]
    code_results: list[Any]
    results: list[Any]

    # Graceful degradation
    docs_retrieval_error: str
    code_retrieval_error: str
    retrieval_warning: str

    # Final
    answerability: str
    answer: str
    sources: list[dict]

    # HITL
    action_approved: bool

    # Guardrails
    policy_decision: str
    policy_reason: str

    # Arguments permissions
    validation_decision: str
    validation_reason: str

    # Role permissions
    user_role: str
    authorization_decision: str
    authorization_reason: str

    llm_error: str