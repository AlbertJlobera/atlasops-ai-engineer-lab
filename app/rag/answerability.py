from app.models import llm
from app.prompts import ANSWERABILITY_PROMPT
from app.rag.context import build_context


def judge_answerability(
    question,
    results,
    tool_messages,
) -> str:

    context = build_context(results)

    tool_context = "\n\n".join(
        (
            f"Tool: {message.name}\n"
            f"Result: {message.content}"
        )
        for message in tool_messages
    )

    prompt = ANSWERABILITY_PROMPT.format(
        question=question,
        context=(
            context
            or "No RAG evidence available."
        ),
        tool_evidence=(
            tool_context
            or "No tool evidence available."
        ),
    )

    response = llm.invoke(prompt)

    return response.content.strip()