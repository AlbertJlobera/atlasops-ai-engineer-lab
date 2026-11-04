from pathlib import Path

from app.code.ingestion import build_code_documents
from app.db.vector_store import get_vector_store
from app.config import CODE_COLLECTION


CODEBASE_PATH = Path("codebase")


def rebuild_code_index():
    # Primero construimos los documentos
    documents = build_code_documents(CODEBASE_PATH)

    # Obtenemos la colección actual y la eliminamos
    code_vector_store = get_vector_store(CODE_COLLECTION)
    code_vector_store.delete_collection()

    # Recreamos/accedemos de nuevo a la colección
    code_vector_store = get_vector_store(CODE_COLLECTION)

    # Indexamos el código
    code_vector_store.add_documents(documents)

    print(f"Indexed {len(documents)} code chunks.")


if __name__ == "__main__":
    rebuild_code_index()