from fastapi import APIRouter, Depends, HTTPException, status, Header
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from database import get_db
from models import User, UserPreference
from config import settings
import uuid

# Helper Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Union[uuid.UUID, int, str]
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PreferenceUpdate(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    preferred_brands: Optional[List[str]] = None

# Security config - Using Argon2 instead of bcrypt to avoid 72-byte limit
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Dependency
async def get_current_user(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    if not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Handle UUID vs Int ID
    try:
        # Try as UUID first if it looks like one
        uid = uuid.UUID(user_id)
        result = await db.execute(select(User).where(User.id == uid))
    except ValueError:
        # Fallback to int if not UUID
        try:
            uid = int(user_id)
            result = await db.execute(select(User).where(User.id == uid))
        except ValueError:
            raise credentials_exception

    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

# Router
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=dict)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing user
    result = await db.execute(select(User).where((User.email == user_in.email) | (User.username == user_in.username)))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    hashed_password = get_password_hash(user_in.password)
    # User ID is auto-generated via default=uuid.uuid4 in model
    new_user = User(username=user_in.username, email=user_in.email, password_hash=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create default preferences
    new_pref = UserPreference(user_id=new_user.id)
    db.add(new_pref)
    await db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "message": "User registered successfully",
        "token": access_token,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }

@router.post("/login", response_model=dict)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.get("/profile", response_model=dict)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    preferences = result.scalars().first()

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at
        },
        "preferences": {
            "min_price": preferences.min_price if preferences else 0,
            "max_price": preferences.max_price if preferences else 10000,
            "currency": preferences.currency if preferences else "USD",
            "language": preferences.language if preferences else "en"
        }
    }

@router.put("/preferences")
async def update_preferences(pref_in: PreferenceUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == current_user.id))
    preferences = result.scalars().first()

    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)

    if pref_in.min_price is not None:
        preferences.min_price = pref_in.min_price
    if pref_in.max_price is not None:
        preferences.max_price = pref_in.max_price
    if pref_in.currency is not None:
        preferences.currency = pref_in.currency
    if pref_in.language is not None:
        preferences.language = pref_in.language
    if pref_in.preferred_brands is not None:
        import json
        preferences.preferred_brands = json.dumps(pref_in.preferred_brands)
        
    await db.commit()
    return {"message": "Preferences updated successfully"}
