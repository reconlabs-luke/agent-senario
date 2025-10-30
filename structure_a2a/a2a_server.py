from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils.errors import ServerError, UnsupportedOperationError
from a2a.utils import new_agent_text_message
from langchain_core.messages import HumanMessage
from agents.langgraph_agent import graph

class LanggraphAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = graph

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        print(f"Context: {context}")
        prompt = context.get_user_input()
        print(f"query: {prompt}")
        response = ""
        for chunk in graph.stream({"messages": [HumanMessage(content=prompt)]}, stream_mode="values"):
            chunk["messages"][-1].pretty_print()
            response = chunk["messages"][-1].content
        print(f"result: {response}")
        await event_queue.enqueue_event(new_agent_text_message(text=response))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())
        
    
agent_executor = LanggraphAgentExecutor()

skill = AgentSkill(
    id="canvas_agent",
    name="canvas_agent",
    description="A canvas agent",
    tags=["canvas", "qa"],
)

agent_card = AgentCard(
    name="canvas_agent",
    description="A canvas agent",
    skills=[skill],
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    url="http://localhost:8000",
    version="1.0.0",
)

request_handler = DefaultRequestHandler(agent_executor=agent_executor, task_store=InMemoryTaskStore())

server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler   
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server.build(), host="0.0.0.0", port=8000)
