import anyio

from pathlib import Path
from langchain.mcp import MCPAdapter

from app.models import llm


async def main():
    server_path = Path("mcp_servers/operations_server.py")

    async with MCPAdapter(server_path) as adapter:
        tools = await adapter.list_tools()

        print("LANGCHAIN TOOLS:")
        for tool in tools:
            print("- name:", tool.name)
            print("  description:", tool.description)
            print("  args:", tool.args)

        llm_with_tools = llm.bind_tools(tools)

        response = await llm_with_tools.ainvoke(
            "How is calculation-service doing right now?"
        )

        print("\nTOOL CALLS:")
        print(response.tool_calls)


if __name__ == "__main__":
    anyio.run(main)