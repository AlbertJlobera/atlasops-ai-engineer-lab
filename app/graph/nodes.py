from langgraph.types import interrupt
from app.graph.state import RAGState
from app.prompts import SOURCE_ROUTE_PROMPT
from app.rag.answerability import judge_answerability
from app.rag.sources import build_sources
from app.rag.retrieval import retrieve_code, retrieve_docs
from app.models import llm
from app.graph.schemas import SourceRouteDecision
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage,
    ToolMessage,
)
from app.rag.context import build_context

import os


def human_approval_node(state: RAGState) -> dict:
    last_message = state["messages"][-1]

    tool_call = last_message.tool_calls[0]

    approved = interrupt({
        "type": "tool_approval",
        "tool": tool_call["name"],
        "args": tool_call["args"],
        "message": "Do you approve this action?"
    })

    if approved:
        return {
            "action_approved": True
        }

    return {
        "action_approved": False,
        "messages": [
            ToolMessage(
                content="Tool execution denied by human reviewer.",
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            )
        ]
    }

def prepare_turn_node(state):
    return {
        "messages": [
            HumanMessage(
                content=state["question"]
            )
        ],

        "docs_results": [],
        "code_results": [],
        "results": [],

        "docs_retrieval_error": "",
        "code_retrieval_error": "",
        "retrieval_warning": "",

        "answerability": "",
        "answer": "",
        "sources": [],

        "action_approved": False,

        "llm_error": "",
    }


def answerability_node(state: RAGState) -> dict:
    question = state["question"]
    results = state.get("results", [])
    messages = state.get("messages", [])

    # Buscamos dónde empieza el turno actual
    last_human_index = 0

    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            last_human_index = i
            break

    # Solo mensajes del turno actual
    current_turn_messages = messages[last_human_index:]

    # Solo ToolMessages del turno actual
    tool_messages = [
        message
        for message in current_turn_messages
        if isinstance(message, ToolMessage)
    ]

    answerability = judge_answerability(
        question,
        results,
        tool_messages
    )

    return {
        "answerability": answerability
    }

def no_answer_node(state: RAGState) -> dict:
    return {
        "answer": "I'm sorry, but I cannot provide an answer to your question based on the available information.",
        "sources": []
    }

def source_router_node(state: RAGState) -> dict:
    question = state.get(
        "standalone_question",
        state["question"]
    )

    structured_llm = llm.with_structured_output(SourceRouteDecision)

    response = structured_llm.invoke([
        ("system", SOURCE_ROUTE_PROMPT),
        ("user", question)
    ])

    return {
        "source_route": response.source_route
    }

def docs_retrieve_node(state):
    question = state.get(
        "standalone_question",
        state["question"]
    )

    try:
        results = retrieve_docs(question)

        return {
            "docs_results": results,
            "docs_retrieval_error": ""
        }

    except Exception as error:
        return {
            "docs_results": [],
            "docs_retrieval_error": (
                f"{type(error).__name__}: {error}"
            )
        }

def code_retrieve_node(state):
    question = state.get(
        "standalone_question",
        state["question"]
    )

    try:
        results = retrieve_code(
            question
        )

        return {
            "code_results": results,
            "code_retrieval_error": ""
        }

    except Exception as error:
        return {
            "code_results": [],
            "code_retrieval_error": (
                f"{type(error).__name__}: {error}"
            )
        }

def use_docs_results_node(state: RAGState) -> dict:
    return {
        "results": state["docs_results"]
    }

def use_code_results_node(state: RAGState) -> dict:
    return {
        "results": state["code_results"]
    }

def merge_results_node(state):

    docs_results = state.get(
        "docs_results",
        []
    )

    code_results = state.get(
        "code_results",
        []
    )

    docs_error = state.get(
        "docs_retrieval_error",
        ""
    )

    code_error = state.get(
        "code_retrieval_error",
        ""
    )

    warning = ""

    if docs_error and not code_error:
        warning = (
            "Document retrieval is temporarily unavailable. "
            "The answer can only use code evidence."
        )

    elif code_error and not docs_error:
        warning = (
            "Code retrieval is temporarily unavailable. "
            "The answer can only use documentation evidence."
        )

    elif docs_error and code_error:
        warning = (
            "Both document and code retrieval are "
            "temporarily unavailable."
        )

    return {
        "results": (
            docs_results
            + code_results
        ),
        "retrieval_warning": warning,
    }

def build_agent_node(tools):
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: RAGState) -> dict:
        messages = state["messages"]
        results = state.get("results", [])

        rag_context = build_context(results)

        # Encontramos el HumanMessage que inicia el turno actual
        last_human_index = 0

        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_index = i
                break

        # ---------------------------
        # HISTORIAL ANTERIOR
        # ---------------------------

        previous_messages = messages[:last_human_index]

        conversation_history = []

        for message in previous_messages:

            # Conservamos preguntas anteriores
            if isinstance(message, HumanMessage):
                conversation_history.append(message)

            # Conservamos solo respuestas finales del agente.
            # Quitamos AIMessage que únicamente pedían ejecutar tools.
            elif (
                isinstance(message, AIMessage)
                and not message.tool_calls
                and message.content
            ):
                conversation_history.append(message)

        # ---------------------------
        # TURNO ACTUAL
        # ---------------------------

        # Aquí SÍ mantenemos absolutamente todo:
        # HumanMessage, AI tool_call y ToolMessage.
        current_turn_messages = messages[last_human_index:]

        agent_messages = (
            conversation_history
            + current_turn_messages
        )

        retrieval_warning = state.get(
            "retrieval_warning",
            ""
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

            # Simulación para tests de robustez.
            # En producción normalmente será "false".
            simulate_llm_failure = (
                os.getenv(
                    "SIMULATE_LLM_FAILURE",
                    "false"
                ).lower()
                == "true"
            )

            if simulate_llm_failure:
                raise RuntimeError(
                    "Simulated LLM API failure."
                )

            response = llm_with_tools.invoke(
                [system_message]
                + agent_messages
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

def llm_failure_node(state):

    return {
        "answer": (
            "I couldn't process the request because "
            "the AI service is temporarily unavailable. "
            "Please try again later."
        ),
        "sources": [],
    }

def finalize_answer_node(state):

    answer = state["messages"][-1].content

    retrieval_warning = state.get(
        "retrieval_warning",
        ""
    )

    if retrieval_warning:
        answer = (
            f"{answer}\n\n"
            f"Warning: {retrieval_warning}"
        )

    return {
        "answer": answer,
        "sources": build_sources(
            state.get("results", [])
        )
    }

def rewrite_question_node(state: RAGState) -> dict:
    question = state["question"]
    messages = state.get("messages", [])

    previous_messages = messages[:-1]

    if not previous_messages:
        return {
            "standalone_question": question
        }

    history = []

    for message in previous_messages:
        if isinstance(message, HumanMessage):
            history.append(
                f"User: {message.content}"
            )

        elif (
            isinstance(message, AIMessage)
            and not message.tool_calls
            and message.content
        ):
            history.append(
                f"Assistant: {message.content}"
            )

    conversation = "\n".join(history)

    prompt = f"""
        Rewrite the user's latest question as a standalone question
        that can be understood without the conversation history.

        Use the conversation history only to resolve references
        to entities, identifiers, people, services, objects or concepts
        mentioned previously.

        Rules:
        - Preserve specific names, identifiers and technical terms
        from the conversation when they are relevant.
        - Resolve ambiguous references such as "it", "that", "this",
        "that error", "the service", "the previous one", etc.
        - Do not answer the question.
        - Do not add information that is not present in the conversation.
        - If a reference cannot be resolved confidently, preserve the
        original wording rather than guessing.
        - If the latest question is already standalone, return it unchanged.
        - Return only the rewritten question.

        Conversation history:
        {conversation}

        Latest question:
        {question}

        Standalone question:
        """
    response = llm.invoke(prompt)

    return {
        "standalone_question": response.content.strip()
    }

def action_denied_node(state: RAGState) -> dict:
    return {
        "answer": "The requested action was not executed because human approval was denied.",
        "sources": []
    }

def action_policy_node(state: RAGState) -> dict:
    last_message = state["messages"][-1]

    tool_call = last_message.tool_calls[0]

    tool_name = tool_call["name"]
    args = tool_call["args"]

    if tool_name == "restart_service":

        service_name = args.get("service_name")

        if service_name == "database-service":
            return {
                "policy_decision": "blocked",
                "policy_reason": (
                    "Restarting database-service is prohibited by policy."
                )
            }
        return {
            "policy_decision": "requires_approval",
            "policy_reason": (
                "Restarting a service requires human approval."
            )
        }
    return {
        "policy_decision": "allowed",
        "policy_reason": "Action is allowed."
    }

def action_blocked_node(state: RAGState) -> dict:
    reason = state.get(
        "policy_reason",
        "The action was blocked by policy."
    )

    return {
        "answer": reason,
        "sources": []
    }

def validate_action_node(state: RAGState) -> dict:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    tool_name = tool_call["name"]
    args = tool_call["args"]

    if tool_name == "restart_service":
        service_name = args.get("service_name")

        allowed_services = {
            "calculation-service",
            "database-service",
        }

        if service_name not in allowed_services:
            return {
                "validation_decision": "invalid",
                "validation_reason": (
                    f"Unknown service: {service_name}"
                )
            }

    return {
        "validation_decision": "valid",
        "validation_reason": ""
    }

def action_invalid_node(state: RAGState) -> dict:
    reason = state.get(
        "validation_reason",
        "The requested action is invalid."
    )

    return {
        "answer": reason,
        "sources": []
    }

def authorize_action_node(state: RAGState) -> dict:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    tool_name = tool_call["name"]
    user_role = state.get("user_role", "viewer")
    if tool_name == "restart_service":
        if user_role not in {"operator", "admin"}:
            return {
                "authorization_decision": "forbidden",
                "authorization_reason": (
                    f"Role '{user_role}' is not allowed to restart services."
                )
            }

    return {
        "authorization_decision": "allowed",
        "authorization_reason": ""
    }

def action_unauthorized_node(state: RAGState) -> dict:
    reason = state.get(
        "authorization_reason",
        "You are not authorized to perform this action."
    )

    return {
        "answer": reason,
        "sources": []
    }

def tool_failure_node(state):
    failed_tools = []

    for message in reversed(state["messages"]):

        if not isinstance(message, ToolMessage):
            break

        if getattr(message, "status", None) == "error":
            failed_tools.append(
                message.name or "unknown_tool"
            )

    tool_names = ", ".join(
        reversed(failed_tools)
    )

    return {
        "answer": (
            "I couldn't retrieve the requested operational "
            "information because the following tool failed: "
            f"{tool_names}. "
            "The information is temporarily unavailable."
        ),
        "sources": [],
    }

def retrieval_failure_node(state):

    docs_error = state.get(
        "docs_retrieval_error",
        ""
    )

    code_error = state.get(
        "code_retrieval_error",
        ""
    )

    if docs_error and code_error:
        source = "document and code"

    elif docs_error:
        source = "document"

    elif code_error:
        source = "code"

    else:
        source = "knowledge"

    return {
        "answer": (
            f"I couldn't retrieve the requested {source} "
            "knowledge because the retrieval service is "
            "temporarily unavailable."
        ),
        "sources": [],
    }

def docs_retrieve_both_node(state):
    question = state.get(
        "standalone_question",
        state["question"]
    )

    try:
        results = retrieve_docs(question)

        return {
            "docs_results": results,
            "docs_retrieval_error": ""
        }

    except Exception as error:
        return {
            "docs_results": [],
            "docs_retrieval_error": (
                f"{type(error).__name__}: {error}"
            )
        }

def code_retrieve_both_node(state):
    question = state.get(
        "standalone_question",
        state["question"]
    )

    try:
        results = retrieve_code(question)

        return {
            "code_results": results,
            "code_retrieval_error": ""
        }

    except Exception as error:
        return {
            "code_results": [],
            "code_retrieval_error": (
                f"{type(error).__name__}: {error}"
            )
        }