from pathlib import Path

from app.models import llm
from app.prompts import RAG_ANSWER_PROMPT
from app.rag.retrieval import retrieve
from app.rag.answerability import judge_answerability
from app.rag.context import build_context


def build_sources(results):
    sources = []

    for doc, score in results:
        sources.append(
            {
                "source": Path(doc.metadata.get("source", "")).name,
                "section": doc.metadata.get("section"),
                "subsection": doc.metadata.get("subsection"),
                "score": score,
            }
        )

    return sources


def generate_answer(question, results):
    context = build_context(results)

    prompt = RAG_ANSWER_PROMPT.format(
        question=question,
        context=context,
    )

    response = llm.invoke(prompt)

    return response.content.strip()


def ask_rag(question: str, k: int = 3):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # 1. Retrieval
    results = retrieve(
        question=question,
        k=k,
    )

    # 2. Answerability
    answerability = judge_answerability(
        question=question,
        results=results,
    )

    # 3. Safe no-answer
    if answerability == "NOT_ANSWERABLE":
        return {
            "question": question,
            "answerable": False,
            "answer": (
                "I don't have enough information in the AtlasOps "
                "documentation to answer that question."
            ),
            "sources": [],
        }

    # 4. Grounded generation
    answer = generate_answer(
        question=question,
        results=results,
    )

    # 5. Sources
    sources = build_sources(results)

    return {
        "question": question,
        "answerable": True,
        "answer": answer,
        "sources": sources,
    }