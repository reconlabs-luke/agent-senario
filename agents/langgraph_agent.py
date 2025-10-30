from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

@tool
def get_canvas_name():
    """Get canvas name tool"""
    return "My Canvas Name is 'Recon Canvas'"

tools = []
tools += [get_canvas_name]

llm = init_chat_model("openai:gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

def canvas_node(state: MessagesState):
    agent = create_agent(
        model=llm_with_tools, 
        tools = tools, 
        system_prompt="You're a helpful Canvas assistant.", 
    )
    response = agent.invoke(state)
    message = response["messages"][-1].content

    return {"messages": [message]}

tool_node = ToolNode(tools)

graph_builder = StateGraph(MessagesState)

graph_builder.add_edge(START, canvas_node.__name__)
graph_builder.add_node(canvas_node.__name__, canvas_node)
graph_builder.add_node("tool_node", tool_node)

graph_builder.add_conditional_edges(canvas_node.__name__, canvas_node, tools_condition)
graph_builder.add_edge("tool_node", canvas_node.__name__)

graph = graph_builder.compile()

if __name__ == "__main__":
    prompt = "Hello, Im Luke. Please get my canvas name."
    response = ""
    for chunk in graph.stream({"messages": [HumanMessage(content=prompt)]}, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
        response = chunk["messages"][-1].content
        
    print("✅ Got Response: ", response)
