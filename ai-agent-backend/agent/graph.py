from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from config import settings
from .tools import search_products, add_to_cart, view_cart
import logging

logger = logging.getLogger(__name__)

# Define State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    cart_items: List[str]
    current_step: str

# Initialize LLM based on provider
def get_llm():
    provider = settings.LLM_PROVIDER.lower()

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in settings")
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0
        )
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in settings")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0
        )
    else:
        # Fallback or error
        raise ValueError(f"Unsupported LLM provider for Agent Graph: {provider}")

try:
    llm = get_llm()
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    # Fallback to avoid import crash, though runtime will fail
    llm = ChatOpenAI(api_key="invalid", model="gpt-3.5-turbo")

# Bind tools
tools = [search_products, add_to_cart, view_cart]
llm_with_tools = llm.bind_tools(tools)

# Define Nodes
def agent_node(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile()
