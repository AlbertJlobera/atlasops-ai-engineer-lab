import os

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from app.graph.state import RAGState
from app.models import llm
from app.rag.context import build_context


def build_agent_node(tools):
    llm_with_tools = llm.bind_tools(
        tools
    )

    def agent_node(
        state: RAGState,
    ) -> dict:

        messages = state["messages"]
        results = state.get(
            "results",
            [],
        )

        rag_context = build_context(
            results
        )

        last_human_index = 0

        for i in range(
            len(messages) - 1,
            -1,
            -1,
        ):
            if isinstance(
                messages[i],
                HumanMessage,
            ):
                last_human_index = i
                break

        previous_messages = (
            messages[:last_human_index]
        )

        conversation_history = []

        for message in previous_messages:

            if isinstance(
                message,
                HumanMessage,
            ):
                conversation_history.append(
                    message
                )

            elif (
                isinstance(
                    message,
                    AIMessage,
                )
                and not message.tool_calls
                and message.content
            ):
                conversation_history.append(
                    message
                )

        current_turn_messages = (
            messages[last_human_index:]
        )

        agent_messages = (
            conversation_history
            + current_turn_messages
        )

        retrieval_warning = state.get(
            "retrieval_warning",
            "",
        )

        system_message = SystemMessage(
            content=f"""
You are AtlasOps, an internal operations AI assistant.

Use the following internal RAG evidence when relevant:

{rag_context if rag_context else "No RAG evidence available."}

Retrieval status:

{retrieval_warning or "All requested knowledge sources are available."}

Use conversation history to understand references and context.

Use available tools whenever current runtime or operational
information is required.

Current health, logs, errors, warnings, CPU, memory,
database pool usage and error rates must be obtained
from the appropriate tool.

Do not invent information that is not supported by
RAG evidence or tool results.

If a retrieval warning is present:

- answer only using the evidence that is still available
- do not invent information from the unavailable source
- clearly tell the user that part of the requested knowledge
  could not be retrieved

If a tool returns a TOOL_ERROR, do not invent the missing
information and do not repeatedly call the same failing tool.

Explain that the requested operational information is
temporarily unavailable.
"""
        )

        try:
            simulate_llm_failure = (
                os.getenv(
                    "SIMULATE_LLM_FAILURE",
                    "false",
                ).lower()
                == "true"
            )

            if simulate_llm_failure:
                raise RuntimeError(
                    "Simulated LLM API failure."
                )

            response = (
                llm_with_tools.invoke(
                    [system_message]
                    + agent_messages
                )
            )

            return {
                "messages": [response],
                "llm_error": "",
            }

        except Exception as error:
            return {
                "llm_error": (
                    f"{type(error).__name__}: "
                    f"{error}"
                )
            }

    return agent_node