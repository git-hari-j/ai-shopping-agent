from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    preferences = relationship('UserPreference', back_populates='user', lazy="selectin")
    search_history = relationship('SearchHistory', back_populates='user', lazy="selectin")
    favorites = relationship('Favorite', back_populates='user', lazy="selectin")
    price_alerts = relationship('PriceAlert', back_populates='user', lazy="selectin")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid, ForeignKey('users.id'), nullable=False)
    min_price = Column(Float, default=0)
    max_price = Column(Float, default=10000)
    preferred_brands = Column(Text)  # JSON string
    preferred_categories = Column(Text)  # JSON string
    currency = Column(String(3), default='USD')
    language = Column(String(5), default='en')

    user = relationship('User', back_populates='preferences')

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid, ForeignKey('users.id'), nullable=False)
    query = Column(String(200), nullable=False)
    budget = Column(Float)
    results_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='search_history')

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid, ForeignKey('users.id'), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_url = Column(Text, nullable=False)
    price = Column(Float)
    platform = Column(String(50))
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favorites')

class PriceAlert(Base):
    __tablename__ = "price_alert"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid, ForeignKey('users.id'), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_url = Column(Text, nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime)

    user = relationship('User', back_populates='price_alerts')
