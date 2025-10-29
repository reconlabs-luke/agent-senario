from mcp.server.fastmcp import FastMCP
from agents.langgraph_agent import graph

mcp = FastMCP(host="0.0.0.0", port=8000, stateless_http=True)


@mcp.tool()
def canvas_agent_tool(prompt: str) -> str:
    """Run the LangGraph canvas agent with a user prompt.

    Args:
        prompt: Natural language instruction or query for the canvas agent.

    Returns:
        The agent's textual response.
    """
    return graph.invoke(prompt)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
