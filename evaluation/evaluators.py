from langchain_core.messages import AIMessage, ToolMessage


def get_called_tools(messages):
    called_tools = []

    for message in messages:
        if isinstance(message, AIMessage):

            for tool_call in message.tool_calls:
                called_tools.append(
                    tool_call["name"]
                )

    return called_tools

def get_called_tools(messages):
    called_tools = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                called_tools.append(
                    tool_call["name"]
                )

    return called_tools


def has_tool_error(messages) -> bool:
    for message in messages:
        if isinstance(message, ToolMessage):
            if getattr(
                message,
                "status",
                None
            ) == "error":
                return True

    return False

def has_empty_results(results) -> bool:
    return len(results) == 0

def has_retrieval_error(result) -> bool:
    return bool(
        result.get(
            "docs_retrieval_error",
            ""
        )
    )

def has_code_retrieval_error(result) -> bool:
    return bool(
        result.get(
            "code_retrieval_error",
            ""
        )
    )

def has_retrieval_warning(result) -> bool:
    return bool(
        result.get(
            "retrieval_warning",
            ""
        )
    )


def has_docs_and_code_failure(result) -> bool:
    return bool(
        result.get(
            "docs_retrieval_error",
            ""
        )
    ) and bool(
        result.get(
            "code_retrieval_error",
            ""
        )
    )

def answer_contains_warning(result) -> bool:
    warning = result.get(
        "retrieval_warning",
        ""
    )

    answer = result.get(
        "answer",
        ""
    )

    if not warning:
        return False

    return warning in answer


def answer_mentions_both_retrieval_failures(result) -> bool:
    answer = result.get(
        "answer",
        ""
    ).lower()

    return (
        "document and code"
        in answer
    )

def has_llm_error(result) -> bool:
    return bool(
        result.get(
            "llm_error",
            ""
        )
    )