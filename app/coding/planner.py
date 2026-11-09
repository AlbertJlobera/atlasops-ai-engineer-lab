from pydantic import BaseModel, Field

from app.coding.schemas import CodeChangeProposal
from app.connectors.github import (
    GITHUB_REPO,
    get_file_content,
    list_repository_files,
)
from app.models import llm
from app.rag.retrieval import retrieve_code


class CodeChangeDraft(BaseModel):
    proposed_content: str = Field(
        description=(
            "Complete content of the file after applying "
            "the requested change."
        )
    )

    reason: str = Field(
        description="Why this change should be made."
    )

    summary: str = Field(
        description="Short human-readable summary of the change."
    )


def _select_candidate_file(
    instruction: str,
) -> str:

    results = retrieve_code(
        instruction,
        k=5,
    )

    if not results:
        raise ValueError(
            "No relevant source code was found "
            "for the requested change."
        )

    best_document, _ = results[0]

    file_path = (
        best_document.metadata.get("path")
    )

    if not file_path:
        raise ValueError(
            "The retrieved code chunk does not "
            "contain a repository path."
        )

    return file_path


def _load_github_file(
    file_path: str,
):
    repository_files = (
        list_repository_files()
    )

    for github_file in repository_files:
        if github_file.path == file_path:
            return get_file_content(
                github_file
            )

    raise FileNotFoundError(
        f"File not found in GitHub repository: "
        f"{file_path}"
    )


def create_code_change_proposal(
    instruction: str,
) -> CodeChangeProposal:

    # 1. Locate relevant file using Code RAG
    file_path = _select_candidate_file(
        instruction
    )

    # 2. Fetch authoritative version from GitHub
    github_file = _load_github_file(
        file_path
    )

    if github_file.content is None:
        raise ValueError(
            f"GitHub file has no content: "
            f"{file_path}"
        )

    # 3. Generate proposed modification
    structured_llm = (
        llm.with_structured_output(
            CodeChangeDraft
        )
    )

    prompt = f"""
You are a software engineering agent working on the
GitHub repository:

{GITHUB_REPO}

The user requested the following code change:

{instruction}

The relevant file is:

{file_path}

Current file content:

{github_file.content}

Produce a proposed new version of this file.

Rules:

- Apply only the requested change.
- Preserve unrelated code.
- Do not invent additional requirements.
- Do not modify other files.
- Return the COMPLETE resulting file content.
- Do not add markdown fences to proposed_content.
- Keep the change as small as reasonably possible.
"""

    draft = structured_llm.invoke(
        prompt
    )

    if draft is None:
        raise RuntimeError(
            "The coding LLM did not return "
            "a valid CodeChangeDraft."
        )

    # 4. Build proposal using trusted GitHub metadata
    return CodeChangeProposal(
        file_path=file_path,
        reason=draft.reason,
        original_sha=github_file.sha,
        original_content=github_file.content,
        proposed_content=draft.proposed_content,
        summary=draft.summary,
    )