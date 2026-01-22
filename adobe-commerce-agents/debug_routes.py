from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage

# Import from agent.graph now, as they are defined there
# Note: In agent.graph, they are SubAgent definitions (TypedDicts), not compiled graphs.
# The 'deepagents' library compiles them internally when creating the deep agent.
# However, for debugging individual agents, we might need to compile them or use the SubAgent spec.
# Looking at deepagents docs (from memory/previous steps), SubAgent is just a spec.
# We cannot 'ainvoke' a SubAgent dict directly.
# We might need to wrap them in create_react_agent or create_deep_agent(subagents=[...]) to test individually,
# OR we simply remove these debug routes if they are not compatible with the new architecture easily.
# Given the user wants "Deep Agent Routing", debugging individual spokes might require the supervisor routing.

# BUT, to fix the import error quickly and preserve functionality if possible:
# We can't invoke the TypedDict.
# Let's inspect how to run a SubAgent standalone.
# If deepagents doesn't expose a standalone runner easily, I will disable these routes or
# create temporary agents for them.

# BETTER APPROACH:
# The `SubAgent` definition in `graph.py` contains `tools` and `system_prompt`.
# We can use `langgraph.prebuilt.create_react_agent` here to instantiate them on the fly for debugging.

from agent.graph import catalog_agent as catalog_spec
from agent.graph import cart_agent as cart_spec
from agent.graph import account_agent as account_spec
from agent.graph import checkout_agent as checkout_spec
from agent.utils import get_llm
from langgraph.prebuilt import create_react_agent

router = APIRouter(prefix="/api/debug", tags=["Debug"])

llm = get_llm()

class AgentRequest(BaseModel):
    message: str
    history: List[dict] = []

class AgentResponse(BaseModel):
    response: str
    full_state: str # Changed to str to be safe

async def run_sub_agent_spec(agent_spec, message: str):
    # Create a transient agent for debugging using the spec
    # SubAgent spec has: name, description, system_prompt, tools
    agent = create_react_agent(
        model=llm,
        tools=agent_spec['tools'],
        prompt=agent_spec['system_prompt'] # Assuming 'prompt' kwarg works as per my previous fix
    )

    messages = [HumanMessage(content=message)]
    result = await agent.ainvoke({"messages": messages})
    last_msg = result['messages'][-1].content
    return {"response": last_msg, "full_state": str(result)}

@router.post("/catalog", response_model=AgentResponse)
async def debug_catalog(req: AgentRequest):
    return await run_sub_agent_spec(catalog_spec, req.message)

@router.post("/cart", response_model=AgentResponse)
async def debug_cart(req: AgentRequest):
    return await run_sub_agent_spec(cart_spec, req.message)

@router.post("/account", response_model=AgentResponse)
async def debug_account(req: AgentRequest):
    return await run_sub_agent_spec(account_spec, req.message)

@router.post("/checkout", response_model=AgentResponse)
async def debug_checkout(req: AgentRequest):
    return await run_sub_agent_spec(checkout_spec, req.message)
