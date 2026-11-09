import os

from functools import lru_cache

from app.config import (
    CODE_COLLECTION,
    DOCS_COLLECTION,
)

from app.db.vector_store import (
    get_vector_store,
)


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
    k: int = 3,
):
    if (
        os.getenv(
            "SIMULATE_EMPTY_DOCS",
            "false",
        ).lower()
        == "true"
    ):
        return []

    if (
        os.getenv(
            "SIMULATE_DOCS_FAILURE",
            "false",
        ).lower()
        == "true"
    ):
        raise RuntimeError(
            "Simulated document retrieval failure."
        )

    vector_store = (
        get_docs_vector_store()
    )

    return (
        vector_store
        .similarity_search_with_score(
            question.strip(),
            k=k,
        )
    )


def retrieve_code(
    question: str,
    k: int = 3,
):
    if (
        os.getenv(
            "SIMULATE_CODE_FAILURE",
            "false",
        ).lower()
        == "true"
    ):
        raise RuntimeError(
            "Simulated code retrieval failure."
        )

    vector_store = (
        get_code_vector_store()
    )

    return (
        vector_store
        .similarity_search_with_score(
            question.strip(),
            k=k,
            filter={
                "provider": "github"
            },
        )
    )