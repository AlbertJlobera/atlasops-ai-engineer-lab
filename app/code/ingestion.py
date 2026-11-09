from pathlib import Path, PurePosixPath
import ast

from langchain_core.documents import Document


# =========================================================
# LOCAL FILE HELPERS
# =========================================================

def load_python_files(path):
    return list(
        Path(path).rglob("*.py")
    )


def get_module_name(
    file_path,
    root_path
):
    return (
        file_path
        .relative_to(root_path)
        .with_suffix("")
        .as_posix()
        .replace("/", ".")
    )


def parse_python_file(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        source = f.read()

    tree = ast.parse(source)

    return source, tree


# =========================================================
# GENERIC SOURCE PARSING
# =========================================================

def get_module_name_from_path(
    source_path: str
) -> str:

    return (
        PurePosixPath(source_path)
        .with_suffix("")
        .as_posix()
        .replace("/", ".")
    )


def extract_code_chunks_from_source(
    source_code: str,
    source_path: str,
):
    """
    Parse Python source code already loaded in memory.

    This is the core AST ingestion logic and does not care
    whether the code came from GitHub, the local filesystem,
    or another external source.
    """

    tree = ast.parse(
        source_code
    )

    module_name = (
        get_module_name_from_path(
            source_path
        )
    )

    chunks = []
    module_code = []

    lines = (
        source_code.splitlines()
    )

    for node in tree.body:

        # =====================================================
        # FUNCTIONS / ASYNC FUNCTIONS / CLASSES
        # =====================================================

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            )
        ):

            start_line = (
                node.lineno - 1
            )

            end_line = (
                node.end_lineno
            )

            code_chunk = (
                lines[
                    start_line:end_line
                ]
            )

            chunks.append(
                {
                    "module": (
                        module_name
                    ),

                    "name": (
                        node.name
                    ),

                    "type": (
                        type(node).__name__
                    ),

                    "code": (
                        "\n".join(
                            code_chunk
                        )
                    ),

                    "start_line": (
                        start_line + 1
                    ),

                    "end_line": (
                        end_line
                    ),
                }
            )

        # =====================================================
        # MODULE-LEVEL VARIABLES / CONSTANTS
        # =====================================================

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            )
        ):

            start_line = (
                node.lineno - 1
            )

            end_line = (
                node.end_lineno
            )

            module_code.extend(
                lines[
                    start_line:end_line
                ]
            )

    # =========================================================
    # MODULE CHUNK
    # =========================================================

    if module_code:

        chunks.append(
            {
                "module": (
                    module_name
                ),

                "name": (
                    module_name
                ),

                "type": (
                    "module"
                ),

                "code": (
                    "\n".join(
                        module_code
                    )
                ),

                "start_line": None,
                "end_line": None,
            }
        )

    return chunks


# =========================================================
# LOCAL INGESTION
# =========================================================

def extract_code_chunks(
    file_path,
    root_path
):
    """
    Backwards-compatible local filesystem ingestion.
    """

    source, _ = (
        parse_python_file(
            file_path
        )
    )

    source_path = (
        file_path
        .relative_to(root_path)
        .as_posix()
    )

    return (
        extract_code_chunks_from_source(
            source_code=source,
            source_path=source_path,
        )
    )


def build_code_documents(
    root_path
):
    """
    Existing local ingestion.

    Kept temporarily while AtlasOps transitions to GitHub.
    """

    root_path = Path(
        root_path
    )

    python_files = (
        load_python_files(
            root_path
        )
    )

    all_documents = []

    for file_path in python_files:

        source_path = (
            file_path
            .relative_to(root_path)
            .as_posix()
        )

        chunks = (
            extract_code_chunks(
                file_path,
                root_path,
            )
        )

        for chunk in chunks:

            document = Document(
                page_content=(
                    chunk["code"]
                ),

                metadata={
                    "source": (
                        file_path.name
                    ),

                    "path": (
                        source_path
                    ),

                    "module": (
                        chunk["module"]
                    ),

                    "symbol": (
                        chunk["name"]
                    ),

                    "symbol_type": (
                        chunk["type"]
                    ),

                    # Keep this because the rest of AtlasOps
                    # identifies these documents as code.
                    "source_type": (
                        "code"
                    ),

                    # New metadata
                    "provider": (
                        "local"
                    ),

                    "sha": None,

                    "start_line": (
                        chunk[
                            "start_line"
                        ]
                    ),

                    "end_line": (
                        chunk[
                            "end_line"
                        ]
                    ),
                }
            )

            all_documents.append(
                document
            )

    return all_documents


# =========================================================
# GITHUB INGESTION
# =========================================================

def build_code_documents_from_github(
    github_files,
    repository: str | None = None,
):
    """
    Build LangChain Documents from GitHubFile objects.

    Expected GitHubFile attributes:
        path
        sha
        size
        content
    """

    all_documents = []

    for github_file in github_files:

        if not github_file.content:
            continue

        chunks = (
            extract_code_chunks_from_source(
                source_code=(
                    github_file.content
                ),
                source_path=(
                    github_file.path
                ),
            )
        )

        for chunk in chunks:

            document = Document(
                page_content=(
                    chunk["code"]
                ),

                metadata={
                    "source": (
                        PurePosixPath(
                            github_file.path
                        ).name
                    ),

                    "path": (
                        github_file.path
                    ),

                    "module": (
                        chunk["module"]
                    ),

                    "symbol": (
                        chunk["name"]
                    ),

                    "symbol_type": (
                        chunk["type"]
                    ),

                    # Important:
                    # remains "code" so existing AtlasOps
                    # routing / source logic keeps working.
                    "source_type": (
                        "code"
                    ),

                    # New origin metadata
                    "provider": (
                        "github"
                    ),

                    "repository": (
                        repository
                    ),

                    # Critical for incremental sync
                    "sha": (
                        github_file.sha
                    ),

                    "size": (
                        github_file.size
                    ),

                    "start_line": (
                        chunk[
                            "start_line"
                        ]
                    ),

                    "end_line": (
                        chunk[
                            "end_line"
                        ]
                    ),
                }
            )

            all_documents.append(
                document
            )

    return all_documents