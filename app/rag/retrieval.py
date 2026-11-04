import os

from functools import lru_cache

from app.db.vector_store import get_vector_store
from app.config import (
    DOCS_COLLECTION,
    CODE_COLLECTION,
)


DEFAULT_K = 3
CODE_DEFAULT_K = 3


@lru_cache(maxsize=1)
def get_docs_vector_store():
    return get_vector_store(
        DOCS_COLLECTION
    )


@lru_cache(maxsize=1)
def get_code_vector_store():
    return get_vector_store(
        CODE_COLLECTION
    )


def retrieve_docs(
    question: str,
    k=DEFAULT_K
):
    if (
        os.getenv(
            "SIMULATE_EMPTY_DOCS",
            "false"
        ).lower()
        == "true"
    ):
        return []

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

    vector_store = (
        get_docs_vector_store()
    )

    return (
        vector_store
        .similarity_search_with_score(
            question.strip(),
            k=k,
            filter={
                "legacy": False
            },
        )
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

    vector_store = (
        get_code_vector_store()
    )

    return (
        vector_store
        .similarity_search_with_score(
            question.strip(),
            k=k,
        )
    )