
from mcp.server.fastmcp import FastMCP
from uuid import uuid4

# Create the MCP server
mcp = FastMCP("CareConnect IT Support")


@mcp.tool()
def create_support_ticket(issue_type: str, description: str) -> dict:
    """Create a demonstration hospital IT support ticket."""

    ticket_id = "IT-" + uuid4().hex[:8].upper()

    return {
        "ticket_id": ticket_id,
        "issue_type": issue_type,
        "description": description,
        "status": "Demo ticket created",
        "message": "No real IT ticket has been submitted."
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
