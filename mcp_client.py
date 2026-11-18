
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def create_ticket_async(issue_type, description):
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve().parent / "mcp_server.py")]
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "create_support_ticket",
                arguments={
                    "issue_type": issue_type,
                    "description": description
                }
            )

            if result.isError:
                raise RuntimeError("MCP ticket tool failed")

            if result.structuredContent:
                return result.structuredContent

            return json.loads(result.content[0].text)


def create_mcp_ticket(issue_type, description):
    return asyncio.run(
        create_ticket_async(issue_type, description)
    )
