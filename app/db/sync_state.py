import json

from sqlalchemy import create_engine, text

from app.config import CONNECTION


engine = create_engine(
    CONNECTION,
    pool_pre_ping=True,
)


def ensure_sync_state_table():
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS source_sync_state (
                    provider VARCHAR(255) NOT NULL,
                    source_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    vector_ids JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                    PRIMARY KEY (provider, source_id)
                )
                """
            )
        )


def get_sync_states(
    provider: str,
) -> dict[str, dict]:

    ensure_sync_state_table()

    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT
                    source_id,
                    version,
                    vector_ids
                FROM source_sync_state
                WHERE provider = :provider
                """
            ),
            {
                "provider": provider
            },
        ).mappings().all()

    return {
        row["source_id"]: {
            "version": row["version"],
            "vector_ids": row["vector_ids"],
        }
        for row in rows
    }


def upsert_sync_state(
    provider: str,
    source_id: str,
    version: str,
    vector_ids: list[str],
):

    ensure_sync_state_table()

    vector_ids_json = json.dumps(
        vector_ids
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO source_sync_state (
                    provider,
                    source_id,
                    version,
                    vector_ids,
                    updated_at
                )
                VALUES (
                    :provider,
                    :source_id,
                    :version,
                    CAST(:vector_ids AS JSONB),
                    NOW()
                )

                ON CONFLICT (
                    provider,
                    source_id
                )

                DO UPDATE SET
                    version = EXCLUDED.version,
                    vector_ids = EXCLUDED.vector_ids,
                    updated_at = NOW()
                """
            ),
            {
                "provider": provider,
                "source_id": source_id,
                "version": version,
                "vector_ids": vector_ids_json,
            },
        )


def delete_sync_state(
    provider: str,
    source_id: str,
):

    ensure_sync_state_table()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DELETE FROM source_sync_state
                WHERE provider = :provider
                AND source_id = :source_id
                """
            ),
            {
                "provider": provider,
                "source_id": source_id,
            },
        )