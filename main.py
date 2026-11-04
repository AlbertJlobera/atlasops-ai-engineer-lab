import anyio

from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.workflow import build_workflow


async def main():

    server_path = Path(
        "mcp_servers/operations_server.py"
    )

    transport = PythonStdioTransport(
        str(server_path)
    )

    client = Client(
        transport
    )

    checkpointer = InMemorySaver()

    async with MCPAdapter(
        client
    ) as adapter:

        tools = await adapter.list_tools()

        graph = build_workflow(
            tools,
            checkpointer
        )

        config = {
            "configurable": {
                "thread_id": "local-user"
            }
        }

        while True:

            question = input(
                "\nYou: "
            ).strip()

            if question.lower() in {
                "exit",
                "quit",
            }:
                break

            result = await graph.ainvoke(
                {
                    "question": question,
                    "user_role": "operator",
                },
                config=config,
            )

            print(
                "\nAtlasOps:",
                result.get(
                    "answer",
                    ""
                )
            )


if __name__ == "__main__":
    anyio.run(main)