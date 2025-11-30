from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

from config import settings
from database import engine, Base, get_db
from models import User
from auth import router as auth_router, get_current_user
from agent.service import run_agent
from core.logging_middleware import DetailedLoggingMiddleware

# Initialize logging
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="AI Shopping Agent",
    description="Backend API for AI Shopping Agent",
    version="3.0.0",
    lifespan=lifespan
)

# Add Logging Middleware first to capture everything
app.add_middleware(DetailedLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# Models
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    response: str
    # Future: return structured products for the UI columns

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        response_text = await run_agent(req.message, req.history)
        return ChatResponse(response=str(response_text))
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "3.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
