import os
import anyio

from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from langchain.mcp import MCPAdapter
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.workflow import build_workflow


async def run_health_test(
    simulate_failure: bool,
    thread_id: str
):
    server_path = Path(
        "mcp_servers/operations_server.py"
    )

    # Copiamos el entorno actual y añadimos
    # explícitamente nuestra variable de prueba.
    mcp_env = os.environ.copy()

    mcp_env["SIMULATE_HEALTH_FAILURE"] = (
        "true"
        if simulate_failure
        else "false"
    )

    # Transporte MCP explícito.
    # Ahora controlamos qué variables recibe
    # el subprocess del servidor.
    transport = PythonStdioTransport(
        str(server_path),
        env=mcp_env
    )

    client = Client(transport)

    checkpointer = InMemorySaver()

    async with MCPAdapter(client) as adapter:

        mcp_tools = await adapter.list_tools()

        compiled = build_workflow(
            mcp_tools,
            checkpointer
        )

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        question = (
            "How is calculation-service doing right now?"
        )

        result = await compiled.ainvoke(
            {
                "question": question,
                "user_role": "viewer"
            },
            config=config
        )

        print(f"\nQuestion: {question}")

        # ==============================================
        # TOOL MESSAGES
        # ==============================================

        print("\nTOOL MESSAGES:")

        tool_messages = [
            message
            for message in result.get(
                "messages",
                []
            )
            if isinstance(
                message,
                ToolMessage
            )
        ]

        if not tool_messages:
            print("No ToolMessages found.")

        for message in tool_messages:
            print(
                f"\nTool: {message.name}"
            )

            print(
                f"Status: "
                f"{getattr(message, 'status', None)}"
            )

            print(
                f"Result: {message.content}"
            )

        # ==============================================
        # FINAL ANSWER
        # ==============================================

        print("\nANSWER:")

        print(
            result.get(
                "answer",
                "No answer generated."
            )
        )


async def main():

    # =====================================================
    # TEST 1 - NORMAL
    # =====================================================

    print("\n")
    print("======================================")
    print("TEST 1 - NORMAL TOOL EXECUTION")
    print("======================================")

    await run_health_test(
        simulate_failure=False,
        thread_id="health-normal-test"
    )

    # =====================================================
    # TEST 2 - FAILURE
    # =====================================================

    print("\n")
    print("======================================")
    print("TEST 2 - TOOL FAILURE")
    print("======================================")

    await run_health_test(
        simulate_failure=True,
        thread_id="health-failure-test"
    )


if __name__ == "__main__":
    anyio.run(main)