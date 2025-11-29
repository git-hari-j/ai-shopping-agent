from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env first
load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the DIY Financial Planner application.
    """

    # Database settings
    DATABASE_URL: str = "postgresql://pguser:pgpass@localhost:5432/finplanner"
    TOP_K: int = 40  # updated from 20

    # Ollama LLM settings
    OLLAMA_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3.2"

    # LLM Provider Switch
    LLM_PROVIDER: str = "groq"  # Options: "ollama", "azure", "groq", "openai", "gemini"

    # OpenRouter settings (legacy compatibility)
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_KEY: str | None = None
    OPENROUTER_MODEL: str | None = None

    # Groq settings
    GROQ_API_URL: str = "https://api.groq.com/openai/v1"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # or "gpt-4o", "gpt-3.5-turbo"

    # Google Gemini settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"  # or "gemini-1.5-pro"

    # Azure OpenAI settings (legacy compatibility)
    AZURE_OAI_KEY: str = "your-azure-openai-key"
    AZURE_OAI_ENDPOINT: str = "your-azure-openai-endpoint"
    AZURE_OAI_DEPLOYMENT: str = "your-azure-openai-deployment"

    # FastAPI / JWT settings
    SECRET_KEY: str = "your-secret-key-for-jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Tell Pydantic where to load env vars from
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Create global settings object
settings = Settings()


class AuthSettings(BaseSettings):
    authjwt_secret_key: str = settings.SECRET_KEY
