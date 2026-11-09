from app.coding.patch import build_unified_diff
from app.coding.planner import create_code_change_proposal
from app.coding.validation import validate_code_change_proposal

from app.graph.state import RAGState
from app.coding.publisher import (
    publish_code_change,
)

from app.coding.schemas import (
    CodeChangeProposal,
)


def propose_code_change_node(
    state: RAGState,
) -> dict:

    instruction = state.get(
        "standalone_question",
        state["question"],
    )

    try:
        proposal = create_code_change_proposal(
            instruction
        )

        validation = (
            validate_code_change_proposal(
                proposal
            )
        )

        diff = build_unified_diff(
            proposal
        )

        return {
            "code_change_proposal": (
                proposal.model_dump()
            ),
            "code_change_validation": (
                validation.model_dump()
            ),
            "code_change_diff": diff,
        }

    except Exception as error:
        return {
            "code_change_proposal": None,
            "code_change_validation": {
                "valid": False,
                "reason": (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                "changed_file": None,
            },
            "code_change_diff": "",
        }

def present_code_change_node(
    state: RAGState,
) -> dict:

    validation = state.get(
        "code_change_validation"
    )

    diff = state.get(
        "code_change_diff",
        "",
    )

    proposal = state.get(
        "code_change_proposal"
    )

    if (
        not validation
        or not validation.get("valid")
    ):
        reason = (
            validation.get("reason")
            if validation
            else "Unknown validation error."
        )

        return {
            "answer": (
                "The proposed code change was rejected "
                f"during validation: {reason}"
            ),
            "sources": [],
        }

    return {
        "answer": (
            f"Proposed code change:\n\n"
            f"File: {proposal['file_path']}\n"
            f"Summary: {proposal['summary']}\n"
            f"Validation: {validation['reason']}\n\n"
            f"Diff:\n{diff}"
        ),
        "sources": [],
    }

def prepare_code_change_action_node(
    state: RAGState,
) -> dict:

    proposal = state.get(
        "code_change_proposal"
    )

    validation = state.get(
        "code_change_validation"
    )

    if (
        not proposal
        or not validation
        or not validation.get("valid")
    ):
        return {
            "pending_action": None
        }

    return {
        "pending_action": {
            "name": "modify_github_code",
            "args": {
                "file_path": proposal["file_path"],
                "original_sha": proposal["original_sha"],
                "summary": proposal["summary"],
            },
        }
    }


def code_change_ready_node(
    state: RAGState,
) -> dict:

    proposal = state[
        "code_change_proposal"
    ]

    return {
        "answer": (
            "The code change was approved.\n\n"
            f"File: {proposal['file_path']}\n"
            f"Summary: {proposal['summary']}\n\n"
            "GitHub has NOT been modified yet. "
            "The repository write step is not connected yet."
        ),
        "sources": [],
    }

def publish_code_change_node(
    state: RAGState,
) -> dict:

    proposal_data = state.get(
        "code_change_proposal"
    )

    if not proposal_data:
        return {
            "code_publish_result": None,
            "code_publish_error": (
                "Missing code change proposal."
            ),
            "answer": (
                "The code change could not be "
                "published because the proposal "
                "is missing."
            ),
            "sources": [],
        }

    try:
        proposal = (
            CodeChangeProposal.model_validate(
                proposal_data
            )
        )

        result = publish_code_change(
            proposal
        )

        return {
            "code_publish_result": (
                result.model_dump()
            ),
            "code_publish_error": "",
            "pending_action": None,
            "answer": (
                "The code change was successfully "
                "published to GitHub.\n\n"
                f"Branch: {result.branch}\n"
                f"Commit: {result.commit_sha}\n"
                f"Pull Request: "
                f"#{result.pull_request_number}\n"
                f"{result.pull_request_url}\n\n"
                "The change has NOT been merged "
                "into the base branch."
            ),
            "sources": [],
        }

    except Exception as error:

        return {
            "code_publish_result": None,
            "code_publish_error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "pending_action": None,
            "answer": (
                "The code change was approved, "
                "but publication to GitHub failed.\n\n"
                f"Reason: "
                f"{type(error).__name__}: {error}"
            ),
            "sources": [],
        }