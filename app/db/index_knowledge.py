from app.config import DOCS_COLLECTION
from app.rag.ingestion import build_chunks
from app.db.vector_store import get_vector_store


def rebuild_index():

    chunks = build_chunks()

    vector_store = get_vector_store(DOCS_COLLECTION)

    vector_store.delete_collection()

    vector_store = get_vector_store(DOCS_COLLECTION)

    vector_store.add_documents(chunks)

    print(f"Indexed {len(chunks)} chunks")


if __name__ == "__main__":
    rebuild_index()