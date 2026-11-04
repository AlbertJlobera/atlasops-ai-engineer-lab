import os

from app.db.vector_store import get_vector_store
from app.config import (
    CODE_DEFAULT_K,
    DEFAULT_K,
    DOCS_COLLECTION,
    CODE_COLLECTION,
)


docs_vector_store = get_vector_store(DOCS_COLLECTION)
code_vector_store = get_vector_store(CODE_COLLECTION)


def retrieve_docs(
    question: str,
    k=DEFAULT_K
):
    if (
        os.getenv(
            "SIMULATE_DOCS_FAILURE",
            "false"
        ).lower()
        == "true"
    ):
        raise RuntimeError(
            "Vector store is temporarily unavailable."
        )

    if (
        os.getenv(
            "SIMULATE_EMPTY_DOCS",
            "false"
        ).lower()
        == "true"
    ):
        return []

    return docs_vector_store.similarity_search_with_score(
        question.strip(),
        k=k,
        filter={"legacy": False}
    )


def retrieve_code(
    question: str,
    k=CODE_DEFAULT_K
):
    if (
        os.getenv(
            "SIMULATE_CODE_FAILURE",
            "false"
        ).lower()
        == "true"
    ):
        raise RuntimeError(
            "Code vector store is temporarily unavailable."
        )

    return code_vector_store.similarity_search_with_score(
        question.strip(),
        k=k
    )