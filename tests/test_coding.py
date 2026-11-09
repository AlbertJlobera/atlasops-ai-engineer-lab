from unittest.mock import Mock

from app.coding.publisher import publish_code_change
from app.coding.schemas import CodeChangeProposal
from app.coding.validation import (
    validate_code_change_proposal,
)


def build_proposal(
    original_content: str = (
        "CALCULATION_TIMEOUT_SECONDS = 15\n"
    ),
    proposed_content: str = (
        "CALCULATION_TIMEOUT_SECONDS = 30\n"
    ),
    original_sha: str = "original-sha",
) -> CodeChangeProposal:

    return CodeChangeProposal(
        file_path="config.py",
        reason="Increase timeout.",
        original_sha=original_sha,
        original_content=original_content,
        proposed_content=proposed_content,
        summary=(
            "Changed timeout from 15 to 30 seconds."
        ),
    )


def test_valid_python_change():

    proposal = build_proposal()

    result = validate_code_change_proposal(
        proposal
    )

    assert result.valid is True
    assert result.changed_file == "config.py"


def test_identical_code_is_rejected():

    content = (
        "CALCULATION_TIMEOUT_SECONDS = 15\n"
    )

    proposal = build_proposal(
        original_content=content,
        proposed_content=content,
    )

    result = validate_code_change_proposal(
        proposal
    )

    assert result.valid is False


def test_invalid_python_syntax_is_rejected():

    proposal = build_proposal(
        proposed_content=(
            "CALCULATION_TIMEOUT_SECONDS =\n"
        )
    )

    result = validate_code_change_proposal(
        proposal
    )

    assert result.valid is False


def test_large_code_change_is_rejected():

    original = "\n".join(
        f"value_{index} = {index}"
        for index in range(60)
    )

    proposed = "\n".join(
        f"value_{index} = {index + 100}"
        for index in range(60)
    )

    proposal = build_proposal(
        original_content=original,
        proposed_content=proposed,
    )

    result = validate_code_change_proposal(
        proposal
    )

    assert result.valid is False


def test_publish_code_change_creates_branch_commit_and_pr(
    monkeypatch,
):

    proposal = build_proposal()

    create_branch_mock = Mock()
    update_file_mock = Mock(
        return_value="new-commit-sha"
    )
    create_pr_mock = Mock(
        return_value={
            "number": 42,
            "url": (
                "https://github.com/"
                "example/repo/pull/42"
            ),
        }
    )

    monkeypatch.setattr(
        "app.coding.publisher.get_branch_sha",
        lambda branch: "base-commit-sha",
    )

    monkeypatch.setattr(
        "app.coding.publisher.get_file_sha",
        lambda path, ref: "original-sha",
    )

    monkeypatch.setattr(
        "app.coding.publisher.create_branch",
        create_branch_mock,
    )

    monkeypatch.setattr(
        "app.coding.publisher.update_file",
        update_file_mock,
    )

    monkeypatch.setattr(
        "app.coding.publisher.create_pull_request",
        create_pr_mock,
    )

    result = publish_code_change(
        proposal
    )

    assert result.branch.startswith(
        "atlasops/ai-config-"
    )

    assert (
        result.commit_sha
        == "new-commit-sha"
    )

    assert (
        result.pull_request_number
        == 42
    )

    assert (
        result.pull_request_url
        == (
            "https://github.com/"
            "example/repo/pull/42"
        )
    )

    create_branch_mock.assert_called_once()

    update_file_mock.assert_called_once()

    create_pr_mock.assert_called_once()


def test_publish_aborts_when_file_sha_changed(
    monkeypatch,
):

    proposal = build_proposal(
        original_sha="old-file-sha"
    )

    create_branch_mock = Mock()
    update_file_mock = Mock()
    create_pr_mock = Mock()

    monkeypatch.setattr(
        "app.coding.publisher.get_branch_sha",
        lambda branch: "current-main-sha",
    )

    monkeypatch.setattr(
        "app.coding.publisher.get_file_sha",
        lambda path, ref: "new-file-sha",
    )

    monkeypatch.setattr(
        "app.coding.publisher.create_branch",
        create_branch_mock,
    )

    monkeypatch.setattr(
        "app.coding.publisher.update_file",
        update_file_mock,
    )

    monkeypatch.setattr(
        "app.coding.publisher.create_pull_request",
        create_pr_mock,
    )

    try:
        publish_code_change(
            proposal
        )

        assert False, (
            "Expected RuntimeError "
            "was not raised."
        )

    except RuntimeError as error:

        assert (
            "changed in GitHub"
            in str(error)
        )

    create_branch_mock.assert_not_called()
    update_file_mock.assert_not_called()
    create_pr_mock.assert_not_called()