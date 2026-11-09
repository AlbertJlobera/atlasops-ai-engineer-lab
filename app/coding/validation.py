import ast
from difflib import unified_diff

from app.coding.schemas import (
    CodeChangeProposal,
    CodeChangeValidation,
)


MAX_CHANGED_LINES = 50


def _count_changed_lines(
    proposal: CodeChangeProposal,
) -> int:

    diff = unified_diff(
        proposal.original_content.splitlines(),
        proposal.proposed_content.splitlines(),
    )

    changed_lines = 0

    for line in diff:
        if line.startswith(("+++", "---", "@@")):
            continue

        if line.startswith(("+", "-")):
            changed_lines += 1

    return changed_lines


def validate_code_change_proposal(
    proposal: CodeChangeProposal,
) -> CodeChangeValidation:

    # ==========================================
    # BASIC METADATA
    # ==========================================

    if not proposal.file_path.strip():
        return CodeChangeValidation(
            valid=False,
            reason="The proposal has no file path.",
        )

    if not proposal.original_sha.strip():
        return CodeChangeValidation(
            valid=False,
            reason="The proposal has no original GitHub SHA.",
            changed_file=proposal.file_path,
        )

    # ==========================================
    # CONTENT VALIDATION
    # ==========================================

    if not proposal.original_content.strip():
        return CodeChangeValidation(
            valid=False,
            reason="The original file content is empty.",
            changed_file=proposal.file_path,
        )

    if not proposal.proposed_content.strip():
        return CodeChangeValidation(
            valid=False,
            reason="The proposed file content is empty.",
            changed_file=proposal.file_path,
        )

    if (
        proposal.original_content
        == proposal.proposed_content
    ):
        return CodeChangeValidation(
            valid=False,
            reason="The proposal does not contain any changes.",
            changed_file=proposal.file_path,
        )

    # ==========================================
    # CHANGE SIZE
    # ==========================================

    changed_lines = _count_changed_lines(
        proposal
    )

    if changed_lines > MAX_CHANGED_LINES:
        return CodeChangeValidation(
            valid=False,
            reason=(
                f"The proposal changes {changed_lines} lines, "
                f"which exceeds the limit of "
                f"{MAX_CHANGED_LINES} lines."
            ),
            changed_file=proposal.file_path,
        )

    # ==========================================
    # PYTHON SYNTAX
    # ==========================================

    if proposal.file_path.endswith(".py"):
        try:
            ast.parse(
                proposal.proposed_content
            )

        except SyntaxError as error:
            return CodeChangeValidation(
                valid=False,
                reason=(
                    "The proposed Python code contains "
                    f"a syntax error: {error}"
                ),
                changed_file=proposal.file_path,
            )

    # ==========================================
    # VALID
    # ==========================================

    return CodeChangeValidation(
        valid=True,
        reason=(
            f"Proposal is valid. "
            f"{changed_lines} changed line(s)."
        ),
        changed_file=proposal.file_path,
    )