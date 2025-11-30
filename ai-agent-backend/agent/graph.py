from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from config import settings
from .tools import search_products, add_to_cart, view_cart
import logging

logger = logging.getLogger(__name__)

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
    # Fallback to avoid import crash
    llm = ChatOpenAI(api_key="invalid", model="gpt-3.5-turbo")

# Define tools list
tools = [search_products, add_to_cart, view_cart]

# Create the agent using LangGraph's prebuilt ReAct agent
# This automatically handles:
# 1. Binding tools to the LLM
# 2. The Agent node (calling LLM)
# 3. The Tool node (executing tools)
# 4. The conditional edge (deciding to loop back or end)
app = create_react_agent(llm, tools)
