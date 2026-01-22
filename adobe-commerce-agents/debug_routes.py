from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage
from agent.subgraphs.catalog_agent import catalog_agent
from agent.subgraphs.cart_agent import cart_agent
from agent.subgraphs.account_agent import account_agent
from agent.subgraphs.checkout_agent import checkout_agent

router = APIRouter(prefix="/api/debug", tags=["Debug"])

class AgentRequest(BaseModel):
    message: str
    history: List[dict] = []

class AgentResponse(BaseModel):
    response: str
    full_state: dict

async def run_sub_agent(agent_graph, message: str):
    messages = [HumanMessage(content=message)]
    result = await agent_graph.ainvoke({"messages": messages})
    last_msg = result['messages'][-1].content
    return {"response": last_msg, "full_state": str(result)}

@router.post("/catalog", response_model=AgentResponse)
async def debug_catalog(req: AgentRequest):
    return await run_sub_agent(catalog_agent, req.message)

@router.post("/cart", response_model=AgentResponse)
async def debug_cart(req: AgentRequest):
    return await run_sub_agent(cart_agent, req.message)

@router.post("/account", response_model=AgentResponse)
async def debug_account(req: AgentRequest):
    return await run_sub_agent(account_agent, req.message)

@router.post("/checkout", response_model=AgentResponse)
async def debug_checkout(req: AgentRequest):
    return await run_sub_agent(checkout_agent, req.message)
