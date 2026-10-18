from langchain_postgres import PGVector
from sqlalchemy import create_engine, text


from app.embeddings import embeddings
from app.config import CONNECTION, COLLECTION_NAME




def check_database_connection():
    engine = create_engine(CONNECTION)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True

    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False


def get_vector_store():
    if not check_database_connection():
        raise ConnectionError("PostgreSQL database is not available.")

    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION,
        use_jsonb=True,
    )
