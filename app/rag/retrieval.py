from app.db.vector_store import get_vector_store
from app.config import DEFAULT_K

vector_store = get_vector_store()


def retrieve(question: str, k: int = DEFAULT_K):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    return vector_store.similarity_search_with_score(
        question.strip(),
        k=k,
        filter={"legacy": False}
    )