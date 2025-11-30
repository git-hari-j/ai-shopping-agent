from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from config import settings
from .tools import search_products, add_to_cart, view_cart

# Define State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    cart_items: List[str]
    current_step: str

# Initialize LLM
llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL,
    temperature=0
)

# Bind tools
tools = [search_products, add_to_cart, view_cart]
llm_with_tools = llm.bind_tools(tools)

# Define Nodes
def agent_node(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    # Basic tool execution logic (simulated for simplicity, usually use ToolNode)
    # In a real app, use langgraph.prebuilt.ToolNode
    last_message = state['messages'][-1]
    # Logic to execute tool calls...
    # For now, we will return a mock response to unblock the structure
    return {"messages": [HumanMessage(content="Tool execution simulation")]}

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END) # Simplified for initial deploy

app = workflow.compile()
