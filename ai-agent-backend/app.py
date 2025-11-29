from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

from config import settings
from database import engine, Base, get_db
from models import User, SearchHistory, Favorite, PriceAlert
from auth import router as auth_router, get_current_user
from core.llm import LLMFactory
from enhanced_scraper import EnhancedScraper
from fastapi.concurrency import run_in_threadpool

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown

# Initialize FastAPI app
app = FastAPI(
    title="AI Shopping Agent",
    description="Backend API for AI Shopping Agent",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth Router
app.include_router(auth_router)

# Initialize Scraper
scraper = EnhancedScraper()

# --- Pydantic Models for Requests/Responses ---

class RecommendRequest(BaseModel):
    product: str
    budget: float
    use_nlp: bool = False
    currency: str = "USD"

class Product(BaseModel):
    name: str
    price: float
    rating: float
    image: str
    url: str
    platform: str

class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    budget: float
    results_count: Optional[int]
    timestamp: str  # ISO format

class FavoriteCreate(BaseModel):
    product_name: str
    product_url: str
    price: float
    platform: str

class FavoriteResponse(BaseModel):
    id: int
    product_name: str
    product_url: str
    price: Optional[float]
    platform: Optional[str]
    added_at: str

class PriceAlertCreate(BaseModel):
    product_name: str
    product_url: str
    target_price: float

class PriceAlertResponse(BaseModel):
    id: int
    product_name: str
    product_url: str
    target_price: float
    current_price: Optional[float]
    is_active: bool
    created_at: str

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Shopping Agent Backend is running!",
        "version": "2.0.0"
    }

@app.get("/api/test")
def test():
    return {
        "message": "Backend is working!",
        "available_endpoints": [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/profile",
            "/api/auth/recommend",
            "/api/favorites",
            "/api/price-alerts"
        ]
    }

@app.post("/api/auth/recommend", response_model=List[Product])
async def recommend(
    req: RecommendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not req.product or req.budget <= 0:
        raise HTTPException(status_code=400, detail="Please provide valid product and budget")

    search_query = req.product
    
    # LLM Query Refinement
    if req.use_nlp:
        try:
            llm = LLMFactory.get_llm()
            prompt = f"Convert this user request into a specific product search query for an e-commerce site. Return ONLY the search terms, no quotes or explanation. Request: {req.product}"
            refined_query = await llm.generate(prompt)
            search_query = refined_query.strip()
            logger.info(f"LLM Refined Query: '{req.product}' -> '{search_query}'")
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            # Fallback to original query
            search_query = req.product

    # Scrape Products (run in threadpool to avoid blocking)
    try:
        # Note: scraper.scrape_all_platforms uses ThreadPoolExecutor internally but waits for it.
        # So we wrap the whole call in run_in_threadpool to offload it from the main event loop.
        products = await run_in_threadpool(
            scraper.scrape_all_platforms,
            search_query,
            max_results_per_platform=5
        )
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed. Please try again.")

    # Filter by budget
    filtered_products = [
        p for p in products
        if p.get("price", 0) <= req.budget
    ]
    
    # Sort by price
    filtered_products.sort(key=lambda x: x.get("price", 0))

    # Save search history
    # Create object directly; relationship expects User object if back_populates is used,
    # but setting foreign key ID is safer/easier with async session sometimes.
    # Here we set user_id directly.
    history_entry = SearchHistory(
        user_id=current_user.id,
        query=search_query,
        budget=req.budget,
        results_count=len(filtered_products)
    )
    db.add(history_entry)
    await db.commit()

    return filtered_products[:15]

@app.get("/api/auth/search-history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(desc(SearchHistory.timestamp))
        .limit(10)
    )
    history = result.scalars().all()

    return [
        SearchHistoryResponse(
            id=h.id,
            query=h.query,
            budget=h.budget,
            results_count=h.results_count,
            timestamp=h.timestamp.isoformat()
        ) for h in history
    ]

@app.post("/api/favorites", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    fav: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if exists
    result = await db.execute(
        select(Favorite).where(
            (Favorite.user_id == current_user.id) &
            (Favorite.product_url == fav.product_url)
        )
    )
    if result.scalars().first():
        return {"message": "Already in favorites"}

    new_fav = Favorite(
        user_id=current_user.id,
        product_name=fav.product_name,
        product_url=fav.product_url,
        price=fav.price,
        platform=fav.platform
    )
    db.add(new_fav)
    await db.commit()

    return {"message": "Added to favorites successfully"}

@app.get("/api/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.added_at))
    )
    favorites = result.scalars().all()

    return [
        FavoriteResponse(
            id=f.id,
            product_name=f.product_name,
            product_url=f.product_url,
            price=f.price,
            platform=f.platform,
            added_at=f.added_at.isoformat()
        ) for f in favorites
    ]

@app.delete("/api/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Favorite).where(
            (Favorite.id == favorite_id) &
            (Favorite.user_id == current_user.id)
        )
    )
    favorite = result.scalars().first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}

# Price Alerts Endpoints (migrated logic from price_alerts.py implicitly or explicitly)
@app.post("/api/price-alerts", status_code=status.HTTP_201_CREATED)
async def create_price_alert(
    alert: PriceAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_alert = PriceAlert(
        user_id=current_user.id,
        product_name=alert.product_name,
        product_url=alert.product_url,
        target_price=alert.target_price,
        current_price=None # Will be updated by background job
    )
    db.add(new_alert)
    await db.commit()
    return {"message": "Price alert created"}

@app.get("/api/price-alerts", response_model=List[PriceAlertResponse])
async def get_price_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriceAlert)
        .where(PriceAlert.user_id == current_user.id)
        .order_by(desc(PriceAlert.created_at))
    )
    alerts = result.scalars().all()

    return [
        PriceAlertResponse(
            id=a.id,
            product_name=a.product_name,
            product_url=a.product_url,
            target_price=a.target_price,
            current_price=a.current_price,
            is_active=a.is_active,
            created_at=a.created_at.isoformat()
        ) for a in alerts
    ]

@app.delete("/api/price-alerts/{alert_id}")
async def delete_price_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriceAlert).where(
            (PriceAlert.id == alert_id) &
            (PriceAlert.user_id == current_user.id)
        )
    )
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()

    return {"message": "Price alert deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
