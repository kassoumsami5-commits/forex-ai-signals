"""
مسارات التحليل والإشارات - توليد إشارات التداول
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, Signal, MarketOverview
from ..schemas import (
    SignalRequest, 
    SignalResponse, 
    MarketOverviewResponse,
    LotCalculatorRequest,
    LotCalculatorResponse
)
from ..services.market_data import market_data_service
from ..services.signal_service import enhanced_signal_generator
from ..services.lot_calculator import lot_calculator
from .auth import get_current_user

router = APIRouter(prefix="/signals", tags=["الإشارات والتحليل"])


@router.post("/generate", response_model=SignalResponse)
async def generate_signal(
    request: SignalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    توليد إشارة تداول بناءً على البيانات المطلوبة
    
    Args:
        request: بيانات طلب الإشارة (الرمز، الإطار الزمني، الرصيد، نسبة المخاطر)
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات
    
    Returns:
        تفاصيل الإشارة generated
    """
    # التحقق من الرصيد
    if request.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الرصيد يجب أن يكون أكبر من صفر"
        )
    
    # التحقق من نسبة المخاطر
    if request.risk_percent <= 0 or request.risk_percent > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نسبة المخاطر يجب أن تكون بين 0.1 و 10"
        )
    
    # التحقق من عدد الشموع المطلوب
    candle_count = request.candle_count if request.candle_count else 200
    if candle_count < 100 or candle_count > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="عدد الشموع يجب أن يكون بين 100 و 500"
        )
    
    try:
        # جلب بيانات السوق
        candles = await market_data_service.get_candles(
            symbol=request.symbol,
            timeframe=request.timeframe,
            count=candle_count
        )
        
        if not candles or len(candles) < 100:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="تعذر جلب بيانات السوق الكافية"
            )
        
        # توليد الإشارة باستخدام المحرك المحسن
        signal_result = enhanced_signal_generator.analyze(
            candles=candles,
            balance=request.balance,
            risk_percent=request.risk_percent,
            symbol=request.symbol
        )
        
        # حفظ الإشارة في قاعدة البيانات
        new_signal = Signal(
            user_id=current_user.id,
            symbol=request.symbol,
            signal_type=signal_result.signal_type,
            entry_price=signal_result.entry_price,
            stop_loss=signal_result.stop_loss,
            take_profit_1=signal_result.take_profit_1,
            take_profit_2=signal_result.take_profit_2,
            lot_size=signal_result.lot_size,
            confidence=signal_result.confidence,
            timeframe=request.timeframe,
            status="pending" if signal_result.signal_type != "NO_TRADE" else "rejected",
            explanation=signal_result.explanation,
            indicators_data=signal_result.indicators
        )
        
        db.add(new_signal)
        await db.commit()
        await db.refresh(new_signal)
        
        return SignalResponse(
            id=new_signal.id,
            symbol=new_signal.symbol,
            signal_type=new_signal.signal_type,
            entry_price=new_signal.entry_price,
            stop_loss=new_signal.stop_loss,
            take_profit_1=new_signal.take_profit_1,
            take_profit_2=new_signal.take_profit_2,
            lot_size=new_signal.lot_size,
            confidence=new_signal.confidence,
            timeframe=new_signal.timeframe,
            status=new_signal.status,
            explanation=new_signal.explanation,
            indicators=new_signal.indicators_data,
            trend=signal_result.trend,
            market_condition=getattr(signal_result, 'market_condition', 'UNKNOWN'),
            signal_quality=getattr(signal_result, 'signal_quality', 'LOW'),
            risk_reward_ratio=getattr(signal_result, 'risk_reward_ratio', 0),
            warning_messages=getattr(signal_result, 'warning_messages', []),
            created_at=new_signal.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ أثناء توليد الإشارة: {str(e)}"
        )


@router.get("/history", response_model=List[SignalResponse])
async def get_signals_history(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على سجل الإشارات للمستخدم الحالي
    
    Args:
        symbol: تصفية حسب الرمز
        timeframe: تصفية حسب الإطار الزمني
        status: تصفية حسب الحالة
        limit: عدد النتائج
        offset: نقطة البداية
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات
    
    Returns:
        قائمة الإشارات
    """
    query = select(Signal).where(Signal.user_id == current_user.id)
    
    # تطبيق الفلاتر
    if symbol:
        query = query.where(Signal.symbol == symbol)
    if timeframe:
        query = query.where(Signal.timeframe == timeframe)
    if status:
        query = query.where(Signal.status == status)
    
    # ترتيب حسب التاريخ
    query = query.order_by(desc(Signal.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    return [
        SignalResponse(
            id=s.id,
            symbol=s.symbol,
            signal_type=s.signal_type,
            entry_price=s.entry_price,
            stop_loss=s.stop_loss,
            take_profit_1=s.take_profit_1,
            take_profit_2=s.take_profit_2,
            lot_size=s.lot_size,
            confidence=s.confidence,
            timeframe=s.timeframe,
            status=s.status,
            explanation=s.explanation,
            indicators=s.indicators_data,
            trend=s.trend,
            created_at=s.created_at
        )
        for s in signals
    ]


@router.get("/latest", response_model=List[SignalResponse])
async def get_latest_signals(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على آخر الإشارات generated للمستخدم الحالي
    """
    result = await db.execute(
        select(Signal)
        .where(Signal.user_id == current_user.id)
        .order_by(desc(Signal.created_at))
        .limit(limit)
    )
    signals = result.scalars().all()
    
    return [
        SignalResponse(
            id=s.id,
            symbol=s.symbol,
            signal_type=s.signal_type,
            entry_price=s.entry_price,
            stop_loss=s.stop_loss,
            take_profit_1=s.take_profit_1,
            take_profit_2=s.take_profit_2,
            lot_size=s.lot_size,
            confidence=s.confidence,
            timeframe=s.timeframe,
            status=s.status,
            explanation=s.explanation,
            indicators=s.indicators_data,
            trend=s.trend,
            created_at=s.created_at
        )
        for s in signals
    ]


@router.patch("/{signal_id}/status")
async def update_signal_status(
    signal_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تحديث حالة إشارة (مفعل، مكتمل، ملغي)
    """
    result = await db.execute(
        select(Signal).where(
            Signal.id == signal_id,
            Signal.user_id == current_user.id
        )
    )
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الإشارة غير موجودة"
        )
    
    valid_statuses = ["pending", "active", "completed", "cancelled", "rejected"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"الحالة غير صالحة. الحالات الصالحة: {', '.join(valid_statuses)}"
        )
    
    signal.status = new_status
    await db.commit()
    
    return {"message": "تم تحديث حالة الإشارة بنجاح"}


@router.get("/stats")
async def get_signals_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على إحصائيات الإشارات للمستخدم
    """
    from sqlalchemy import func, and_
    
    # إجمالي الإشارات
    total_result = await db.execute(
        select(func.count(Signal.id)).where(Signal.user_id == current_user.id)
    )
    total_signals = total_result.scalar()
    
    # الإشارات حسب النوع
    buy_result = await db.execute(
        select(func.count(Signal.id)).where(
            and_(Signal.user_id == current_user.id, Signal.signal_type == "BUY")
        )
    )
    buy_count = buy_result.scalar()
    
    sell_result = await db.execute(
        select(func.count(Signal.id)).where(
            and_(Signal.user_id == current_user.id, Signal.signal_type == "SELL")
        )
    )
    sell_count = sell_result.scalar()
    
    # الإشارات حسب الحالة
    active_result = await db.execute(
        select(func.count(Signal.id)).where(
            and_(Signal.user_id == current_user.id, Signal.status == "active")
        )
    )
    active_count = active_result.scalar()
    
    completed_result = await db.execute(
        select(func.count(Signal.id)).where(
            and_(Signal.user_id == current_user.id, Signal.status == "completed")
        )
    )
    completed_count = completed_result.scalar()
    
    # متوسط مستوى الثقة
    avg_conf_result = await db.execute(
        select(func.avg(Signal.confidence)).where(Signal.user_id == current_user.id)
    )
    avg_confidence = avg_conf_result.scalar() or 0
    
    return {
        "total_signals": total_signals,
        "buy_signals": buy_count,
        "sell_signals": sell_count,
        "active_signals": active_count,
        "completed_signals": completed_count,
        "average_confidence": round(float(avg_confidence), 1)
    }


# مسارات السوق
market_router = APIRouter(prefix="/market", tags=["بيانات السوق"])


@market_router.get("/overview")
async def get_market_overview():
    """
    الحصول على نظرة عامة على السوق
    يعرض أسعار الحالي لجميع الأدوات الرئيسية
    """
    try:
        overview = await market_data_service.get_market_overview()
        return {"data": overview}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في جلب بيانات السوق: {str(e)}"
        )


@market_router.get("/price/{symbol}")
async def get_price(symbol: str):
    """
    الحصول على السعر الحالي لزوج عملات محدد
    """
    try:
        price_data = await market_data_service.get_current_price(symbol)
        if not price_data or price_data.get("price") == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"تعذر جلب بيانات السعر للرمز {symbol}"
            )
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في جلب السعر: {str(e)}"
        )


@market_router.get("/candles/{symbol}")
async def get_candles(
    symbol: str,
    timeframe: str = "1h",
    count: int = 100
):
    """
    الحصول على بيانات الشموع التاريخية
    """
    try:
        candles = await market_data_service.get_candles(symbol, timeframe, count)
        if not candles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"تعذر جلب بيانات الشموع للرمز {symbol}"
            )
        return {"symbol": symbol, "timeframe": timeframe, "candles": candles}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في جلب الشموع: {str(e)}"
        )


# مسارات حاسبة اللوت
calculator_router = APIRouter(prefix="/calculator", tags=["حاسبة اللوت"])


@calculator_router.post("/lot-size", response_model=LotCalculatorResponse)
async def calculate_lot_size(request: LotCalculatorRequest):
    """
    حساب حجم اللوت الأمثل بناءً على المخاطر
    
    Args:
        request: بيانات الحساب (الرصيد، نسبة المخاطر، مسافة وقف الخسارة، الرمز)
    
    Returns:
        حجم اللوت والبيانات ذات الصلة
    """
    if request.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الرصيد يجب أن يكون أكبر من صفر"
        )
    
    if request.risk_percent <= 0 or request.risk_percent > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نسبة المخاطر يجب أن تكون بين 0.1 و 100"
        )
    
    if request.stop_loss_pips <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="مسافة وقف الخسارة يجب أن تكون أكبر من صفر"
        )
    
    result = lot_calculator.calculate_lot_size(
        balance=request.balance,
        risk_percent=request.risk_percent,
        stop_loss_pips=request.stop_loss_pips,
        symbol=request.symbol
    )
    
    return LotCalculatorResponse(
        lot_size=result.lot_size,
        risk_amount=result.risk_amount,
        pip_value=result.pip_value,
        stop_loss_pips=result.stop_loss_pips,
        message=result.message
    )


@calculator_router.post("/lot-size-from-prices")
async def calculate_lot_from_prices(
    balance: float,
    risk_percent: float,
    entry_price: float,
    stop_loss_price: float,
    symbol: str = "XAUUSD"
):
    """
    حساب حجم اللوت بناءً على فرق السعر الفعلي
    """
    if balance <= 0 or risk_percent <= 0 or entry_price <= 0 or stop_loss_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="جميع القيم يجب أن تكون أكبر من صفر"
        )
    
    result = lot_calculator.calculate_from_price_difference(
        balance=balance,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        symbol=symbol
    )
    
    return result