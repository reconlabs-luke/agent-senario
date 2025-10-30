from mcp.server.fastmcp import FastMCP
from agents.langgraph_agent import graph
from langchain_core.messages import HumanMessage

mcp = FastMCP(host="0.0.0.0", port=8000, stateless_http=True)


@mcp.tool()
async def canvas_agent_tool(prompt: str) -> str:
    """Run the LangGraph canvas agent with a user prompt.

    Args:
        prompt: Natural language instruction or query for the canvas agent.

    Returns:
        The agent's textual response.
    """
    response = ""
    async for chunk in graph.astream({"messages": [HumanMessage(content=prompt)]}, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
        response = chunk["messages"][-1].content
        
    print("✅ Got Response: ", response)

    return response

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
