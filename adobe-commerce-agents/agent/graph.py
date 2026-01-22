from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from agent.utils import get_llm
from agent.subgraphs.catalog_agent import catalog_agent
from agent.subgraphs.cart_agent import cart_agent
from agent.subgraphs.account_agent import account_agent
from agent.subgraphs.checkout_agent import checkout_agent
import logging

logger = logging.getLogger(__name__)

llm = get_llm()

# --------------------------------------------------------------------
# Define Tools that wrap Sub-Agents
# --------------------------------------------------------------------

@tool
async def catalog_tool(request: str):
    """
    Use this tool for product discovery, searching for items, finding product prices,
    descriptions, and checking availability. Input should be a clear natural language request.
    """
    # We invoke the sub-agent with the specific request
    # The sub-agent has its own state, but we treat it as a stateless function call here
    # passing the request as a new conversation.
    # In a more advanced setup, we might pass history, but for "Delegation", a specific request is best.
    result = await catalog_agent.ainvoke({"messages": [HumanMessage(content=request)]})
    return result["messages"][-1].content

@tool
async def cart_tool(request: str):
    """
    Use this tool for managing the shopping cart.
    Capabilities: Add items, view cart, remove items, merge cart.
    Input should be a clear natural language request (e.g., "Add SKU-123 to cart").
    """
    result = await cart_agent.ainvoke({"messages": [HumanMessage(content=request)]})
    return result["messages"][-1].content

@tool
async def account_tool(request: str):
    """
    Use this tool for user authentication and account management.
    Capabilities: Login, Register, Check status.
    Input should be a clear natural language request.
    """
    result = await account_agent.ainvoke({"messages": [HumanMessage(content=request)]})
    return result["messages"][-1].content

@tool
async def checkout_tool(request: str):
    """
    Use this tool for the checkout process.
    Capabilities: Set shipping/billing address, choose shipping method, payment, place order.
    Do NOT use this for adding items to cart.
    Input should be a clear natural language request.
    """
    result = await checkout_agent.ainvoke({"messages": [HumanMessage(content=request)]})
    return result["messages"][-1].content

# --------------------------------------------------------------------
# Main "Deep" Agent
# --------------------------------------------------------------------

system_prompt = (
    "You are a sophisticated AI Shopping Assistant designed to help users with their e-commerce needs. "
    "You operate as a 'Deep Agent', meaning you should think step-by-step to satisfy complex requests.\n\n"
    "You have access to specialized workers (tools):\n"
    "- catalog_tool: For finding products.\n"
    "- cart_tool: For managing the cart.\n"
    "- account_tool: For login/signup.\n"
    "- checkout_tool: For completing the purchase.\n\n"
    "STRATEGY:\n"
    "1. Analyze the user's request.\n"
    "2. If the request requires multiple steps (e.g., 'Find a laptop and buy it'), break it down.\n"
    "   - First, search for the laptop using catalog_tool.\n"
    "   - Then, ask the user to confirm which one to buy (if ambiguous) or add it using cart_tool.\n"
    "3. Always verify the result of a tool call before proceeding.\n"
    "4. If you need more information from the user, ask them.\n"
    "5. Be helpful, polite, and concise."
)

# create_react_agent creates a graph that loops: Agent -> Tools -> Agent ...
app = create_react_agent(
    llm=llm,
    tools=[catalog_tool, cart_tool, account_tool, checkout_tool],
    state_modifier=system_prompt
)
