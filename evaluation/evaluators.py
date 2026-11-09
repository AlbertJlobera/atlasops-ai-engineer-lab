from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)


def get_called_tools(messages):
    called_tools = []

    for message in messages:
        if isinstance(
            message,
            AIMessage,
        ):
            for tool_call in message.tool_calls:
                called_tools.append(
                    tool_call["name"]
                )

    return called_tools


def has_tool_error(
    messages,
) -> bool:

    for message in messages:
        if isinstance(
            message,
            ToolMessage,
        ):
            if getattr(
                message,
                "status",
                None,
            ) == "error":
                return True

    return False


def has_empty_results(
    results,
) -> bool:
    return len(results) == 0


def has_retrieval_error(
    result,
) -> bool:
    return bool(
        result.get(
            "docs_retrieval_error",
            "",
        )
    )


def has_code_retrieval_error(
    result,
) -> bool:
    return bool(
        result.get(
            "code_retrieval_error",
            "",
        )
    )


def has_retrieval_warning(
    result,
) -> bool:
    return bool(
        result.get(
            "retrieval_warning",
            "",
        )
    )


def has_docs_and_code_failure(
    result,
) -> bool:
    return (
        bool(
            result.get(
                "docs_retrieval_error",
                "",
            )
        )
        and bool(
            result.get(
                "code_retrieval_error",
                "",
            )
        )
    )


def answer_contains_warning(
    result,
) -> bool:

    warning = result.get(
        "retrieval_warning",
        "",
    )

    answer = result.get(
        "answer",
        "",
    )

    if not warning:
        return False

    return warning in answer


def answer_mentions_both_retrieval_failures(
    result,
) -> bool:

    answer = result.get(
        "answer",
        "",
    ).lower()

    return (
        "document and code"
        in answer
    )


def has_llm_error(
    result,
) -> bool:
    return bool(
        result.get(
            "llm_error",
            "",
        )
    )


# =========================================================
# CODING AGENT
# =========================================================


def has_code_change_proposal(
    result,
) -> bool:

    return bool(
        result.get(
            "code_change_proposal"
        )
    )


def code_change_targets_file(
    result,
    expected_file: str,
) -> bool:

    proposal = result.get(
        "code_change_proposal"
    )

    if not proposal:
        return False

    return (
        proposal.get(
            "file_path"
        )
        == expected_file
    )


def has_valid_code_change(
    result,
) -> bool:

    validation = result.get(
        "code_change_validation"
    )

    if not validation:
        return False

    return bool(
        validation.get(
            "valid"
        )
    )


def has_code_change_diff(
    result,
) -> bool:

    diff = result.get(
        "code_change_diff",
        "",
    )

    return bool(
        diff.strip()
    )


def has_human_approval_interrupt(
    result,
    expected_tool: str = (
        "modify_github_code"
    ),
) -> bool:

    interrupts = result.get(
        "__interrupt__",
        [],
    )

    for interrupt_item in interrupts:

        value = getattr(
            interrupt_item,
            "value",
            interrupt_item,
        )

        if (
            isinstance(
                value,
                dict,
            )
            and value.get(
                "tool"
            )
            == expected_tool
        ):
            return True

    return False


def has_code_publish_result(
    result,
) -> bool:

    return bool(
        result.get(
            "code_publish_result"
        )
    )