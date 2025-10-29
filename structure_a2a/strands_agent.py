from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(
    region_name="ap-northeast-2",
    model_id="apac.anthropic.claude-sonnet-4-20250514-v1:0"
)

@tool
def secret_tool(user: str | None = None):
    """Secret tool. It's just saying my secret when user ask me about it."""
    return f"Hello {user or ""}! Im secret tool ! Secret is '원피스는 존재한다'"

tools = []
tools += [secret_tool]
agent = Agent(
            model=model,
            agent_id="genpresso_agent",
            system_prompt="You're a helpful assistant.",
            tools=tools,
        )

if __name__ == "__main__":
    response = agent(prompt="Hello, Im Luke. Please let me know about my secret")
    print("\nResponse : ", response.message["content"][0]["text"])
