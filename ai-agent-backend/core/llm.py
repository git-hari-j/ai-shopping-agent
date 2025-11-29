import logging
import httpx
from typing import List
from langchain_openai import AzureChatOpenAI
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------- Embeddings ----------------
async def get_ollama_embedding(text: str) -> List[float]:
    """Fetch embeddings from Ollama embedding model."""
    try:
        logging.debug(f"[LLM] Generating embeddings via OLLAMA model='{settings.EMBEDDING_MODEL}'")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/embeddings",
                json={"model": settings.EMBEDDING_MODEL, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]
    except Exception as e:
        logging.error(f"[LLM] Embedding generation failed: {e}", exc_info=True)
        raise


# ---------------- LLM Factory ----------------
class LLMFactory:
    @staticmethod
    def get_llm():
        provider = settings.LLM_PROVIDER.lower()
        logging.info(f"[LLMFactory] Initializing LLM provider: {provider}")

        if provider == "azure":
            return AzureOAI_LLM()
        elif provider == "ollama":
            return OllamaLLM()
        elif provider == "groq":
            return GroqLLM()
        elif provider == "openai":
            return OpenAI_LLM()
        elif provider == "gemini":
            return GeminiLLM()
        else:
            raise ValueError(f"[LLMFactory] Unsupported LLM provider: {settings.LLM_PROVIDER}")


# ---------------- Azure OpenAI ----------------
class AzureOAI_LLM:
    """Wrapper for Azure OpenAI LLM."""
    def __init__(self):
        self.client = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OAI_ENDPOINT,
            api_key=settings.AZURE_OAI_KEY,
            azure_deployment=settings.AZURE_OAI_DEPLOYMENT,
            api_version="2023-05-15",
            temperature=0.4,
            streaming=False,
        )
        logging.info("[LLM] Azure OpenAI LLM initialized")

    async def _acall(self, prompt: str) -> str:
        logging.info("[LLM] Sending prompt to Azure OpenAI model")
        response = await self.client.ainvoke(prompt)
        output = response.content if response else ""
        logging.info("[LLM] Azure OpenAI response received")
        return output

    async def generate(self, prompt: str) -> str:
        return await self._acall(prompt)


# ---------------- Ollama ----------------
class OllamaLLM:
    """Wrapper for interacting with Ollama LLM."""
    def __init__(self, model: str = settings.LLM_MODEL, base_url: str = settings.OLLAMA_URL):
        self.model = model
        self.base_url = base_url
        logging.info(f"[LLM] Ollama LLM initialized with model='{model}' at {base_url}")

    async def _acall(self, prompt: str) -> str:
        logging.debug(f"[LLM] Using Ollama model='{self.model}' for prompt generation")
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512,
                    }
                },
            )
            r.raise_for_status()
            response = r.json().get("response", "")
            logging.debug(f"[LLM] Ollama response received (length={len(response)})")
            return response

    async def generate(self, prompt: str) -> str:
        return await self._acall(prompt)


# ---------------- Groq ----------------
class GroqLLM:
    """Wrapper for Groq API (OpenAI-compatible interface)."""
    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_API_URL

        if not self.api_key:
            raise ValueError("[LLM] Missing GROQ_API_KEY in settings or .env file")

        logging.info(f"[LLM] Groq LLM initialized with model='{self.model}'")

    async def _acall(self, prompt: str) -> str:
        logging.debug(f"[LLM] Using Groq model='{self.model}' for prompt generation")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                r.raise_for_status()
                data = r.json()

                content = data["choices"][0]["message"]["content"]
                logging.debug(f"[LLM] Groq response received (length={len(content)})")

                # Log token usage for cost tracking
                usage = data.get("usage", {})
                logging.info(f"[LLM] Groq tokens - prompt: {usage.get('prompt_tokens')}, "
                           f"completion: {usage.get('completion_tokens')}, "
                           f"total: {usage.get('total_tokens')}")

                return content

        except httpx.HTTPStatusError as e:
            logging.error(f"[LLM] Groq API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"[LLM] Groq request failed: {e}", exc_info=True)
            raise

    async def generate(self, prompt: str) -> str:
        return await self._acall(prompt)


# ---------------- OpenAI ----------------
class OpenAI_LLM:
    """Wrapper for OpenAI API."""
    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"

        if not self.api_key:
            raise ValueError("[LLM] Missing OPENAI_API_KEY in settings or .env file")

        logging.info(f"[LLM] OpenAI LLM initialized with model='{self.model}'")

    async def _acall(self, prompt: str) -> str:
        logging.debug(f"[LLM] Using OpenAI model='{self.model}' for prompt generation")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                r.raise_for_status()
                data = r.json()

                content = data["choices"][0]["message"]["content"]
                logging.debug(f"[LLM] OpenAI response received (length={len(content)})")

                # Log token usage for cost tracking
                usage = data.get("usage", {})
                logging.info(f"[LLM] OpenAI tokens - prompt: {usage.get('prompt_tokens')}, "
                           f"completion: {usage.get('completion_tokens')}, "
                           f"total: {usage.get('total_tokens')}")

                return content

        except httpx.HTTPStatusError as e:
            logging.error(f"[LLM] OpenAI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"[LLM] OpenAI request failed: {e}", exc_info=True)
            raise

    async def generate(self, prompt: str) -> str:
        return await self._acall(prompt)


# ---------------- Google Gemini ----------------
class GeminiLLM:
    """Wrapper for Google Gemini API."""
    def __init__(self):
        self.model = settings.GEMINI_MODEL
        self.api_key = settings.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError("[LLM] Missing GEMINI_API_KEY in settings or .env file")

        logging.info(f"[LLM] Gemini LLM initialized with model='{self.model}'")

    async def _acall(self, prompt: str) -> str:
        logging.debug(f"[LLM] Using Gemini model='{self.model}' for prompt generation")

        # Gemini uses a different API format
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
                "topP": 0.95,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()

                # Extract content from Gemini's response format
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        content = candidate["content"]["parts"][0].get("text", "")
                        logging.debug(f"[LLM] Gemini response received (length={len(content)})")

                        # Log token usage if available
                        if "usageMetadata" in data:
                            usage = data["usageMetadata"]
                            logging.info(f"[LLM] Gemini tokens - prompt: {usage.get('promptTokenCount')}, "
                                       f"completion: {usage.get('candidatesTokenCount')}, "
                                       f"total: {usage.get('totalTokenCount')}")

                        return content

                # If response format is unexpected
                logging.error(f"[LLM] Unexpected Gemini response format: {data}")
                return "Error: Unexpected response format from Gemini"

        except httpx.HTTPStatusError as e:
            logging.error(f"[LLM] Gemini API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"[LLM] Gemini request failed: {e}", exc_info=True)
            raise

    async def generate(self, prompt: str) -> str:
        return await self._acall(prompt)
