from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from bedrock_agentcore import BedrockAgentCoreApp

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.workflow import build_workflow


@asynccontextmanager
async def lifespan(app):

    server_path = Path(
        "mcp_servers/operations_server.py"
    )

    transport = PythonStdioTransport(
        str(server_path)
    )

    client = Client(
        transport
    )

    async with AsyncExitStack() as stack:

        adapter = await stack.enter_async_context(
            MCPAdapter(client)
        )

        tools = await adapter.list_tools()

        checkpointer = InMemorySaver()

        graph = build_workflow(
            tools,
            checkpointer
        )

        app.state.graph = graph

        yield


app = BedrockAgentCoreApp(
    lifespan=lifespan
)


@app.entrypoint
async def invoke(
    payload,
    context
):

    question = (
        payload.get("question")
        or payload.get("prompt")
    )

    if (
        not isinstance(question, str)
        or not question.strip()
    ):
        raise ValueError(
            "question must be a non-empty string"
        )

    user_role = payload.get(
        "user_role",
        "viewer"
    )

    if user_role not in {
        "viewer",
        "operator",
        "admin",
    }:
        raise ValueError(
            "user_role must be viewer, operator or admin"
        )

    # AgentCore proporciona un session_id propio.
    # Lo reutilizamos como thread_id de LangGraph.
    session_id = (
        getattr(
            context,
            "session_id",
            None
        )
        or payload.get("thread_id")
        or "agentcore-local"
    )

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    result = await app.state.graph.ainvoke(
        {
            "question": question.strip(),
            "user_role": user_role,
        },
        config=config,
    )

    return {
        "answer": result.get(
            "answer",
            ""
        ),
        "sources": result.get(
            "sources",
            []
        ),
        "session_id": session_id,
    }


if __name__ == "__main__":
    app.run()