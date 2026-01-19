from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from config import settings
import logging

logger = logging.getLogger(__name__)

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
        # Fallback to OpenAI if others are not configured or supported
        logger.warning(f"Unsupported LLM provider for Agents: {provider}. Defaulting to OpenAI.")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0
        )
