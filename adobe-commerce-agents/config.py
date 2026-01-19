from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env first
load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the AI Agent application.
    """
    # Debug Mode
    DEBUG: bool = False

    # Ollama LLM settings
    OLLAMA_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3.2"

    # LLM Provider Switch
    LLM_PROVIDER: str = "azure"  # Options: "ollama", "azure", "groq", "openai", "gemini"

    # Groq settings
    GROQ_API_URL: str = "https://api.groq.com/openai/v1"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Google Gemini settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_DEPLOYMENT_NAME: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2023-05-15"

    # Magento settings
    MAGENTO_URL: str = "https://demo-fklvc3a-qslkp4psgn6ta.us-4.magentosite.cloud/telcob2c"
    MAGENTO_ACCESS_TOKEN: str | None = None

    # Tell Pydantic where to load env vars from
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Create global settings object
settings = Settings()
