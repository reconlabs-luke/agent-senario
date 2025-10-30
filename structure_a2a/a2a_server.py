from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils.errors import ServerError, UnsupportedOperationError
from a2a.utils import new_agent_text_message
from langchain_core.messages import HumanMessage
from agents.langgraph_agent import graph
from envs import *
from stage import Stage


class LanggraphAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = graph

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        print(f"Context: {context}")
        prompt = context.get_user_input()
        print(f"query: {prompt}")
        response = ""
        for chunk in graph.stream(
            {"messages": [HumanMessage(content=prompt)]}, stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
            response = chunk["messages"][-1].content
        print(f"result: {response}")
        await event_queue.enqueue_event(new_agent_text_message(text=response))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())


agent_executor = LanggraphAgentExecutor()

skill = AgentSkill(
    id="canvas_agent",
    name="canvas_agent",
    description="An agent related canvas",
    tags=["canvas", "qa"],
)

agent_card = AgentCard(
    name="canvas_agent",
    description="A canvas agent",
    skills=[skill],
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    url=(
        f"http://localhost:{AGENTCORE_RUNTIME_PORT}"
        if STAGE.lower() == Stage.DEV.value.lower()
        else AGENTCORE_RUNTIME_URL
    ),
    version="1.0.0",
)

request_handler = DefaultRequestHandler(
    agent_executor=agent_executor, task_store=InMemoryTaskStore()
)

from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def ping():
    return {"status": "healthy"}


server = A2AFastAPIApplication(agent_card=agent_card, http_handler=request_handler)
app.mount("/", server.build())

if __name__ == "__main__":
    import uvicorn
    import logging

    logging.basicConfig(level=logging.INFO)

    uvicorn.run(app, host="0.0.0.0", port=int(AGENTCORE_RUNTIME_PORT))
