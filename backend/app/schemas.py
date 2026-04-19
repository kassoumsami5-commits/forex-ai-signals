"""Pydantic schemas for request/response validation - Enhanced for Forex AI Signals."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class SignalType(str, Enum):
    """أنواع الإشارات"""
    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"


class SignalStatus(str, Enum):
    """حالات الإشارات"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class MarketCondition(str, Enum):
    """ظروف السوق"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"


class SignalQuality(str, Enum):
    """جودة الإشارة"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    REJECTED = "REJECTED"


class SubscriptionTier(str, Enum):
    """خطط الاشتراك"""
    FREE = "free"
    PRO = "pro"
    VIP = "vip"


# ==================== Auth Schemas ====================

class UserCreate(BaseModel):
    """تسجيل مستخدم جديد"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('كلمتا المرور غير متطابقتين')
        return v


class LoginRequest(BaseModel):
    """طلب تسجيل الدخول"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """رد رمز الوصول"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class UserResponse(BaseModel):
    """معلومات المستخدم"""
    id: int
    email: str
    full_name: str
    subscription_tier: str
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime


# ==================== Signal Schemas ====================

class SignalRequest(BaseModel):
    """طلب توليد إشارة"""
    symbol: str = Field(
        ..., 
        pattern="^(XAUUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|USDCAD|BTCUSD)$",
        description="رمز السوق"
    )
    timeframe: str = Field(
        ...,
        pattern="^(5min|15min|30min|1h|4h|1day)$",
        description="الإطار الزمني"
    )
    balance: float = Field(..., gt=0, le=10000000, description="رصيد الحساب USD")
    risk_percent: float = Field(
        ..., 
        gt=0, 
        le=10, 
        description="نسبة المخاطر % (0.1-10)"
    )
    candle_count: Optional[int] = Field(
        200, 
        ge=100, 
        le=500, 
        description="عدد الشموع للتحليل"
    )


class SignalResponse(BaseModel):
    """استجابة الإشارة المحسنة"""
    id: int
    symbol: str
    signal_type: str  # BUY, SELL, NO_TRADE
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    lot_size: float
    confidence: float  # 0-100%
    timeframe: str
    status: str  # pending, active, completed, cancelled, rejected
    explanation: str  # تفسير كامل بالعربية
    indicators: Dict[str, Any]  # بيانات المؤشرات الفنية
    trend: str  # BULLISH, BEARISH, NEUTRAL
    market_condition: Optional[str] = "UNKNOWN"  # ظروف السوق
    signal_quality: Optional[str] = "LOW"  # جودة الإشارة
    risk_reward_ratio: Optional[float] = 0  # نسبة المخاطرة/المكافأة
    warning_messages: Optional[List[str]] = []  # رسائل التحذير
    created_at: datetime
    
    class Config:
        from_attributes = True


class SignalHistoryFilters(BaseModel):
    """فلاتر سجل الإشارات"""
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    signal_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ==================== Market Data Schemas ====================

class MarketCardData(BaseModel):
    """بيانات بطاقة السوق"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume: Optional[float] = None
    timestamp: Optional[str] = None


class MarketOverviewResponse(BaseModel):
    """نظرة عامة على السوق"""
    data: List[MarketCardData]
    timestamp: datetime = Field(default_factory=datetime.now)


class PriceResponse(BaseModel):
    """بيانات السعر"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    change_percent: Optional[float] = None
    timestamp: Optional[str] = None


class CandleData(BaseModel):
    """بيانات شمعة واحدة"""
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandlesResponse(BaseModel):
    """استجابة بيانات الشموع"""
    symbol: str
    timeframe: str
    candles: List[CandleData]


# ==================== Calculator Schemas ====================

class LotCalculatorRequest(BaseModel):
    """طلب حساب حجم اللوت"""
    balance: float = Field(..., gt=0, description="رصيد الحساب USD")
    risk_percent: float = Field(..., gt=0, le=100, description="نسبة المخاطر %")
    stop_loss_pips: float = Field(..., gt=0, description="مسافة وقف الخسارة بالنقاط")
    symbol: str = Field(
        default="XAUUSD",
        pattern="^(XAUUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|USDCAD|BTCUSD)$"
    )


class LotCalculatorResponse(BaseModel):
    """نتيجة حساب حجم اللوت"""
    lot_size: float
    risk_amount: float
    pip_value: float
    stop_loss_pips: float
    message: str


# ==================== Subscription Schemas ====================

class SubscriptionPlanResponse(BaseModel):
    """تفاصيل خطة الاشتراك"""
    tier: str
    name: str
    name_ar: str
    price: float
    price_monthly: float
    period_days: Optional[int] = None
    features: List[str]
    limits: Dict[str, Any]


class SubscriptionResponse(BaseModel):
    """معلومات الاشتراك الحالي"""
    tier: str
    name: str
    name_ar: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    features: List[str]
    days_remaining: Optional[int] = None
    auto_renew: bool = False


class SubscribeRequest(BaseModel):
    """طلب الاشتراك"""
    tier: str = Field(..., pattern="^(free|pro|vip)$")
    payment_method: Optional[str] = None
    auto_renew: bool = False


class SubscriptionStatsResponse(BaseModel):
    """إحصائيات الاشتراك"""
    current_tier: str
    days_remaining: Optional[int] = None
    total_signals_used: int
    signals_limit: int  # -1 for unlimited
    limit_type: str  # "daily" or "unlimited"


# ==================== Webhook Schemas ====================

class TradingViewWebhookPayload(BaseModel):
    """Webhook payload من TradingView"""
    symbol: str
    timeframe: Optional[str] = "1h"
    trigger: str  # Buy, Sell, Long, Short, alert
    price: float
    volume: Optional[float] = None
    bar_time: Optional[str] = None
    text: Optional[str] = None


class WebhookResponse(BaseModel):
    """استجابة Webhook"""
    success: bool
    message: str
    signal_id: Optional[int] = None
    confidence: Optional[float] = None


# ==================== Admin Schemas ====================

class AdminDashboardResponse(BaseModel):
    """لوحة تحكم المشرف"""
    total_users: int
    active_users_30d: int
    total_signals: int
    pending_signals: int
    active_subscriptions: int
    subscription_tiers: Dict[str, int]
    today_signals: int
    timestamp: str


class AdminUserResponse(BaseModel):
    """معلومات المستخدم للAdmin"""
    id: int
    email: str
    full_name: str
    subscription_tier: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    signals_count: int = 0


class AdminSignalResponse(BaseModel):
    """معلومات الإشارة للAdmin"""
    id: int
    user_id: int
    symbol: str
    signal_type: str
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    lot_size: float
    confidence: float
    timeframe: str
    status: str
    source: Optional[str] = None
    created_at: datetime


# ==================== Generic Responses ====================

class MessageResponse(BaseModel):
    """رسالة عامة"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """استجابة خطأ"""
    detail: str
    success: bool = False


# ==================== Signal Analysis Schema ====================

class IndicatorData(BaseModel):
    """بيانات مؤشر فني"""
    name: str
    value: float
    description: str
    signal: str  # bullish, bearish, neutral


class SignalAnalysisSummary(BaseModel):
    """ملخص تحليل الإشارة"""
    trend: str
    momentum: str
    market_condition: str
    adx_value: float
    rsi_value: float
    indicators: List[IndicatorData]
    support_levels: List[float]
    resistance_levels: List[float]
    confidence_score: float
    risk_reward_ratio: float
    quality_assessment: str
    arabic_explanation: str