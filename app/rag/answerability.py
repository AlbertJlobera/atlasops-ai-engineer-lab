from app.models import llm
from app.prompts import ANSWERABILITY_PROMPT
from app.rag.context import build_context


def judge_answerability(question, results):
    context = build_context(results)

    prompt = ANSWERABILITY_PROMPT.format(
        question=question,
        context=context,
    )

    response = llm.invoke(prompt)

    return response.content.strip()