import anyio
import sys

from mcp import Client, StdioServerParameters


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["mcp_servers/operations_server.py"]
    )

    async with Client(server) as client:
        tools = await client.list_tools()

        print("AVAILABLE TOOLS:")
        for tool in tools.tools:
            print(f"- {tool.name}")
            print(f"  description: {tool.description}")
            print(f"  schema: {tool.input_schema}")

        result = await client.call_tool(
            "get_service_health",
            {
                "service_name": "calculation-service"
            }
        )

        print("\nTOOL RESULT:")
        print("is_error:", result.is_error)
        print("content:", result.content)
        print("structured_content:", result.structured_content)


if __name__ == "__main__":
    anyio.run(main)