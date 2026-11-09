import uuid

from app.config import (
    CODE_COLLECTION,
)

from app.db.vector_store import (
    get_vector_store,
)

from app.db.sync_state import (
    get_sync_states,
    upsert_sync_state,
    delete_sync_state,
)

from app.connectors.github import (
    GITHUB_OWNER,
    GITHUB_REPO,
    list_repository_files,
    get_file_content,
)

from app.code.ingestion import (
    build_code_documents_from_github,
)


def build_vector_id(
    document,
) -> str:

    metadata = document.metadata

    identity = (
        f"github://"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/"
        f"{metadata['path']}"
        f"?sha={metadata['sha']}"
        f"&symbol={metadata['symbol']}"
        f"&start={metadata['start_line']}"
        f"&end={metadata['end_line']}"
    )

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            identity,
        )
    )


def sync_github_code():

    provider = (
        f"github:"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}"
    )

    vector_store = get_vector_store(
        CODE_COLLECTION
    )

    # =====================================================
    # CURRENT STATE IN POSTGRES
    # =====================================================

    stored_state = get_sync_states(
        provider
    )

    # =====================================================
    # CURRENT STATE IN GITHUB
    # =====================================================

    github_files = (
        list_repository_files()
    )

    current_paths = {
        file.path
        for file in github_files
    }

    created = 0
    updated = 0
    unchanged = 0
    deleted = 0

    # =====================================================
    # NEW / MODIFIED FILES
    # =====================================================

    for github_file in github_files:

        previous = stored_state.get(
            github_file.path
        )

        # ---------------------------------------------
        # UNCHANGED
        # ---------------------------------------------

        if (
            previous
            and previous["version"]
            == github_file.sha
        ):
            unchanged += 1

            print(
                f"[UNCHANGED] "
                f"{github_file.path}"
            )

            continue

        # ---------------------------------------------
        # DOWNLOAD ONLY IF NEW / MODIFIED
        # ---------------------------------------------

        full_file = get_file_content(
            github_file
        )

        documents = (
            build_code_documents_from_github(
                [full_file],
                repository=GITHUB_REPO,
            )
        )

        vector_ids = [
            build_vector_id(document)
            for document in documents
        ]

        # ---------------------------------------------
        # INDEX NEW VERSION
        # ---------------------------------------------

        if documents:

            vector_store.add_documents(
                documents=documents,
                ids=vector_ids,
            )

        # ---------------------------------------------
        # REMOVE OLD VERSION
        # ---------------------------------------------

        if previous:

            old_vector_ids = previous.get(
                "vector_ids",
                []
            )

            if old_vector_ids:
                vector_store.delete(
                    ids=old_vector_ids
                )

            updated += 1

            print(
                f"[UPDATED] "
                f"{github_file.path}"
            )

        else:

            created += 1

            print(
                f"[NEW] "
                f"{github_file.path}"
            )

        # ---------------------------------------------
        # STORE NEW SHA + IDS
        # ---------------------------------------------

        upsert_sync_state(
            provider=provider,
            source_id=github_file.path,
            version=github_file.sha,
            vector_ids=vector_ids,
        )

    # =====================================================
    # FILES REMOVED FROM GITHUB
    # =====================================================

    for path, previous in (
        stored_state.items()
    ):

        if path in current_paths:
            continue

        old_vector_ids = previous.get(
            "vector_ids",
            []
        )

        if old_vector_ids:

            vector_store.delete(
                ids=old_vector_ids
            )

        delete_sync_state(
            provider=provider,
            source_id=path,
        )

        deleted += 1

        print(
            f"[DELETED] {path}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print()
    print(
        "================================"
    )

    print(
        "GITHUB CODE SYNC SUMMARY"
    )

    print(
        "================================"
    )

    print(
        f"New:       {created}"
    )

    print(
        f"Updated:   {updated}"
    )

    print(
        f"Unchanged: {unchanged}"
    )

    print(
        f"Deleted:   {deleted}"
    )

    print(
        f"Total:     {len(github_files)}"
    )


if __name__ == "__main__":
    sync_github_code()