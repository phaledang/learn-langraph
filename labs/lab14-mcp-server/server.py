from mcp.server.fastapi import MCPFastAPI
from mcp.types import Tool, TextContent

app = MCPFastAPI(
    name="local-mcp-server",
    version="0.1.0",
)

# ---- Tool definition ----
@app.tool()
def ping(message: str) -> str:
    """
    Simple health-check tool.
    """
    return f"PONG: {message}"
