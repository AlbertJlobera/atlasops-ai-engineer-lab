import anyio

from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

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

            # =================================================
            # FINAL ANSWER
            # =================================================
            while result.get("__interrupt__"):

                interrupt_data = (
                    result["__interrupt__"][0]
                )

                value = getattr(
                    interrupt_data,
                    "value",
                    interrupt_data,
                )

                print(
                    "\nApproval required:"
                )

                if isinstance(value, dict):

                    print(
                        "Action:",
                        value.get("tool")
                    )

                    if value.get("summary"):
                        print(
                            "Summary:",
                            value["summary"]
                        )

                    if value.get("diff"):
                        print(
                            "\nDiff:\n",
                            value["diff"]
                        )

                decision = input(
                    "\nApprove? [y/N]: "
                ).strip().lower()

                approved = decision in {
                    "y",
                    "yes",
                }

                result = await graph.ainvoke(
                    Command(
                        resume=approved
                    ),
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