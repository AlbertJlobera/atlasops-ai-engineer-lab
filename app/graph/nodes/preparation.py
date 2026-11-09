from langchain_core.messages import AIMessage, HumanMessage

from app.graph.state import RAGState
from app.models import llm


def prepare_turn_node(state: RAGState) -> dict:
    return {
        "messages": [
            HumanMessage(
                content=state["question"]
            )
        ],
        "docs_results": [],
        "code_results": [],
        "results": [],
        "docs_retrieval_error": "",
        "code_retrieval_error": "",
        "retrieval_warning": "",
        "answerability": "",
        "answer": "",
        "sources": [],
        "action_approved": False,
        "llm_error": "",
        "code_change_proposal": None,
        "code_change_diff": "",
        "code_change_validation": None,
        "pending_action": None,
        "code_publish_result": None,
        "code_publish_error": "",
    }


def rewrite_question_node(state: RAGState) -> dict:
    question = state["question"]
    messages = state.get("messages", [])

    previous_messages = messages[:-1]

    if not previous_messages:
        return {
            "standalone_question": question
        }

    history = []

    for message in previous_messages:
        if isinstance(message, HumanMessage):
            history.append(
                f"User: {message.content}"
            )

        elif (
            isinstance(message, AIMessage)
            and not message.tool_calls
            and message.content
        ):
            history.append(
                f"Assistant: {message.content}"
            )

    conversation = "\n".join(history)

    prompt = f"""
Rewrite the user's latest question as a standalone question
that can be understood without the conversation history.

Use the conversation history only to resolve references
to entities, identifiers, people, services, objects or concepts
mentioned previously.

Rules:

- Preserve specific names, identifiers and technical terms
  from the conversation when they are relevant.
- Resolve ambiguous references such as "it", "that", "this",
  "that error", "the service", "the previous one", etc.
- Do not answer the question.
- Do not add information that is not present in the conversation.
- If a reference cannot be resolved confidently, preserve the
  original wording rather than guessing.
- If the latest question is already standalone, return it unchanged.
- Return only the rewritten question.

Conversation history:
{conversation}

Latest question:
{question}

Standalone question:
"""

    response = llm.invoke(prompt)

    return {
        "standalone_question": response.content.strip()
    }