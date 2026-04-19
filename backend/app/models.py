"""SQLAlchemy database models - Updated to match schemas."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    subscription_tier = Column(String(20), default="free")
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    signals = relationship("Signal", back_populates="user", cascade="all, delete-orphan")


class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Symbol and timeframe
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    
    # Signal data
    signal_type = Column(String(20), nullable=False)  # BUY, SELL, NO_TRADE
    status = Column(String(20), default="pending")
    
    # Entry and exit levels
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    
    # Risk management
    lot_size = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Analysis data
    trend = Column(String(20), nullable=True)
    explanation = Column(Text, nullable=True)
    indicators_data = Column(JSON, nullable=True)
    
    # Source
    source = Column(String(50), default="manual")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="signals")


class MarketOverview(Base):
    __tablename__ = "market_overview"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=True)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Webhook data
    provider = Column(String(50), nullable=True)
    event_type = Column(String(50), nullable=True)
    payload = Column(JSON, nullable=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="SET NULL"), nullable=True)
    
    # Processing result
    status = Column(String(20), default="pending")
    validation_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    signal = relationship("Signal")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    tier = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    
    # Billing
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50), default="mock")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
