from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPAgentTool, MCPClient
from mcp.client.streamable_http import streamablehttp_client
from strands.types.collections import PaginatedList
from utils import get_token, get_agent_core_runtime_url
from envs import *
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

model = BedrockModel(
    region_name="ap-northeast-2",
    model_id="apac.anthropic.claude-sonnet-4-20250514-v1:0",
)

REGION = "us-east-1"
MEMORY_ID = "strands_langgraph_intergration-VXxO3uCKU1"
SESSION_ID = "test-session-1"
ACTOR_ID = "test-actor-1"

memory_client = MemoryClient(region_name=REGION)
agentcore_memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=SESSION_ID,
    actor_id=ACTOR_ID
)

session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=agentcore_memory_config,
    region_name="us-east-1"
)



@tool
def secret_tool(user: str | None = None):
    """Secret tool. It's just saying my secret when user ask me about it."""
    return f"Hello {user or ""}! Im secret tool ! Secret is '원피스는 존재한다'"


mcp_url = get_agent_core_runtime_url(AGENTCORE_RUNTIME_MCP_ARN, AWS_REGION)
bearer_token = get_token(
    COGNITO_USER_POOL_ID,
    COGNITO_USERNAME,
    COGNITO_PASSWORD,
    COGNITO_CLIENT_ID,
    AWS_REGION,
)
headers = {
    "Content-Type": "application/json",
    "authorization": f"Bearer {bearer_token}",
}
mcp_client = MCPClient(lambda: streamablehttp_client(mcp_url, headers))
mcp_tools = []
with mcp_client:
    tools: PaginatedList[MCPAgentTool] = mcp_client.list_tools_sync()
    print("✅ Loaded MCP Tools:")
    for t in tools:
        print(f"Tool Name: {t.tool_name}")

    mcp_tools.extend(tools)

    tools = []
    tools += [secret_tool]
    tools += mcp_tools
    agent = Agent(
        model=model,
        agent_id="genpresso_agent",
        system_prompt="You're a helpful assistant.",
        tools=tools,
        session_manager=session_manager,
    )

    # prompt = "Hello, Im Luke. Please get my canvas name. If there are some issues, please show me as log."
    prompt = "Hello, Who am i ?"
    response = agent(
        prompt=prompt
    )

    print("\nResponse : ", response.message["content"][0]["text"])
