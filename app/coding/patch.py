from difflib import unified_diff

from app.coding.schemas import CodeChangeProposal


def build_unified_diff(
    proposal: CodeChangeProposal,
) -> str:

    original_lines = (
        proposal.original_content
        .splitlines(
            keepends=True
        )
    )

    proposed_lines = (
        proposal.proposed_content
        .splitlines(
            keepends=True
        )
    )

    diff = unified_diff(
        original_lines,
        proposed_lines,
        fromfile=(
            f"a/{proposal.file_path}"
        ),
        tofile=(
            f"b/{proposal.file_path}"
        ),
        lineterm="\n",
    )

    return "".join(diff)