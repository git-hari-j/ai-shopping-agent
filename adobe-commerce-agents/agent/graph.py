from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from agent.utils import get_llm
from agent.subgraphs.catalog_agent import catalog_agent
from agent.subgraphs.cart_agent import cart_agent
from agent.subgraphs.account_agent import account_agent
from agent.subgraphs.checkout_agent import checkout_agent
import functools
import logging

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# 1. Define State
# --------------------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str

# --------------------------------------------------------------------
# 2. Define Supervisor
# --------------------------------------------------------------------
members = ["CatalogAgent", "CartAgent", "AccountAgent", "CheckoutAgent"]
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. \n"
    " - Use 'CatalogAgent' for finding products, product details, or checking stock.\n"
    " - Use 'CartAgent' for adding items to cart, viewing cart, or merging carts.\n"
    " - Use 'AccountAgent' for login, registration, or checking customer status.\n"
    " - Use 'CheckoutAgent' for shipping addresses, billing, shipping methods, payments, and placing orders.\n"
    " - Respond with FINISH only when the user's request is fully satisfied or if you need more input from the user."
)

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["CatalogAgent", "CartAgent", "AccountAgent", "CheckoutAgent", "FINISH"]

llm = get_llm()

def supervisor_node(state: AgentState):
    messages = state["messages"]
    # We use structured output to enforce the routing decision
    response = llm.with_structured_output(Router).invoke(
        [
            ("system", system_prompt.format(members=", ".join(members))),
        ] + messages
    )
    next_node = response["next"]

    # If the LLM decides to finish, we might want to ensure the last message isn't just "FINISH"
    # but for this pattern, the routing decision is internal state.
    return {"next": next_node}

# --------------------------------------------------------------------
# 3. Define Graph
# --------------------------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)

# Helper to wrap sub-agents
# The sub-agents are already compiled graphs, so we can invoke them.
# However, they expect their own state schema. Usually compatible with list of messages.
async def call_catalog_agent(state: AgentState):
    result = await catalog_agent.ainvoke(state)
    # We take the last message from the sub-agent and append it
    return {"messages": [result["messages"][-1]]}

async def call_cart_agent(state: AgentState):
    result = await cart_agent.ainvoke(state)
    return {"messages": [result["messages"][-1]]}

async def call_account_agent(state: AgentState):
    result = await account_agent.ainvoke(state)
    return {"messages": [result["messages"][-1]]}

async def call_checkout_agent(state: AgentState):
    result = await checkout_agent.ainvoke(state)
    return {"messages": [result["messages"][-1]]}

workflow.add_node("CatalogAgent", call_catalog_agent)
workflow.add_node("CartAgent", call_cart_agent)
workflow.add_node("AccountAgent", call_account_agent)
workflow.add_node("CheckoutAgent", call_checkout_agent)

# Edges
workflow.add_edge(START, "Supervisor")

# Conditional edges from Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next"],
    {
        "CatalogAgent": "CatalogAgent",
        "CartAgent": "CartAgent",
        "AccountAgent": "AccountAgent",
        "CheckoutAgent": "CheckoutAgent",
        "FINISH": END
    }
)

# Edges from Workers back to Supervisor
workflow.add_edge("CatalogAgent", "Supervisor")
workflow.add_edge("CartAgent", "Supervisor")
workflow.add_edge("AccountAgent", "Supervisor")
workflow.add_edge("CheckoutAgent", "Supervisor")

app = workflow.compile()
