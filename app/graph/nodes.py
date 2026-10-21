from app.graph.state import RAGState
from app.rag.answerability import judge_answerability
from app.rag.pipeline import build_sources, generate_answer
from app.rag.retrieval import retrieve


def retrieve_node(state: RAGState) -> dict:
    question = state["question"]

    results = retrieve(question)

    return {
        "results": results
    }

def answerability_node(state: RAGState) -> dict:
    question = state["question"]
    results = state["results"]

    answerability = judge_answerability(question, results)

    return {
        "answerability": answerability
    }

def generate_node(state: RAGState) -> dict:
    question = state["question"]
    results = state["results"]

    answer = generate_answer(question, results)
    sources = build_sources(results)

    return {
        "answer": answer,
        "sources": sources
    }

def no_answer_node(state: RAGState) -> dict:
    return {
        "answer": "I'm sorry, but I cannot provide an answer to your question based on the available information.",
        "sources": []
    }