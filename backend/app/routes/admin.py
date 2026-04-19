"""
مسارات لوحة التحكم - إدارة المستخدمين والإشارات والإحصائيات
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Signal, Subscription, WebhookLog, PaymentHistory
from ..schemas import (
    AdminUserResponse,
    AdminSignalResponse,
    AdminStatsResponse,
    AdminDashboardResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["الإدارة"])
security = HTTPBearer()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    التحقق من صلاحيات المشرف
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح بالوصول - يتطلب صلاحيات المشرف"
        )
    return current_user


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على إحصائيات لوحة التحكم
    """
    # عدد المستخدمين
    users_count = await db.execute(select(func.count(User.id)))
    total_users = users_count.scalar()
    
    # عدد المستخدمين النشطين (اشتركوا في آخر 30 يوم)
    active_date = datetime.utcnow() - timedelta(days=30)
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= active_date)
    )
    active_users = active_users_result.scalar()
    
    # عدد الإشارات
    signals_count = await db.execute(select(func.count(Signal.id)))
    total_signals = signals_count.scalar()
    
    # الإشارات المعلقة
    pending_signals_result = await db.execute(
        select(func.count(Signal.id)).where(Signal.status == "pending")
    )
    pending_signals = pending_signals_result.scalar()
    
    # عدد الاشتراكات النشطة
    active_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "active")
    )
    active_subscriptions = active_subs_result.scalar()
    
    # إحصائيات الاشتراكات حسب الخطة
    pro_users = await db.execute(
        select(func.count(User.id)).where(User.subscription_tier == "pro")
    )
    pro_count = pro_users.scalar()
    
    vip_users = await db.execute(
        select(func.count(User.id)).where(User.subscription_tier == "vip")
    )
    vip_count = vip_users.scalar()
    
    free_users = await db.execute(
        select(func.count(User.id)).where(User.subscription_tier == "free")
    )
    free_count = free_users.scalar()
    
    # إشارات اليوم
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_signals_result = await db.execute(
        select(func.count(Signal.id)).where(Signal.created_at >= today_start)
    )
    today_signals = today_signals_result.scalar()
    
    return AdminDashboardResponse(
        total_users=total_users,
        active_users_30d=active_users,
        total_signals=total_signals,
        pending_signals=pending_signals,
        active_subscriptions=active_subscriptions,
        subscription_tiers={
            "free": free_count,
            "pro": pro_count,
            "vip": vip_count
        },
        today_signals=today_signals,
        timestamp=datetime.now().isoformat()
    )


@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    tier: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على قائمة المستخدمين
    """
    query = select(User).order_by(desc(User.created_at)).limit(limit).offset(skip)
    
    if tier:
        query = query.where(User.subscription_tier == tier)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        AdminUserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            subscription_tier=u.subscription_tier,
            is_admin=u.is_admin,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login,
            signals_count=0  # سيتم حسابها لاحقاً
        )
        for u in users
    ]


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على تفاصيل مستخدم محدد
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # حساب عدد إشارات المستخدم
    signals_count_result = await db.execute(
        select(func.count(Signal.id)).where(Signal.user_id == user_id)
    )
    signals_count = signals_count_result.scalar()
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        subscription_tier=user.subscription_tier,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
        signals_count=signals_count
    )


@router.patch("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    new_tier: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    تحديث اشتراك مستخدم
    """
    if new_tier not in ["free", "pro", "vip"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الخطة غير صالحة"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user.subscription_tier = new_tier
    await db.commit()
    
    return {"message": "تم تحديث الاشتراك بنجاح", "new_tier": new_tier}


@router.get("/signals", response_model=List[AdminSignalResponse])
async def get_all_signals(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على جميع الإشارات
    """
    query = select(Signal).order_by(desc(Signal.created_at)).limit(limit).offset(skip)
    
    if symbol:
        query = query.where(Signal.symbol == symbol)
    if signal_type:
        query = query.where(Signal.signal_type == signal_type)
    if status:
        query = query.where(Signal.status == status)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    return [
        AdminSignalResponse(
            id=s.id,
            user_id=s.user_id,
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
            source=s.source,
            created_at=s.created_at
        )
        for s in signals
    ]


@router.get("/signals/stats")
async def get_signals_statistics(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على إحصائيات الإشارات
    """
    # الإشارات حسب النوع
    buy_result = await db.execute(
        select(Signal.signal_type, func.count(Signal.id))
        .group_by(Signal.signal_type)
    )
    by_type = {row[0]: row[1] for row in buy_result.all()}
    
    # الإشارات حسب الحالة
    status_result = await db.execute(
        select(Signal.status, func.count(Signal.id))
        .group_by(Signal.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}
    
    # الإشارات حسب الرمز
    symbol_result = await db.execute(
        select(Signal.symbol, func.count(Signal.id))
        .group_by(Signal.symbol)
        .order_by(desc(func.count(Signal.id)))
        .limit(10)
    )
    by_symbol = {row[0]: row[1] for row in symbol_result.all()}
    
    # متوسط الثقة
    avg_confidence = await db.execute(
        select(func.avg(Signal.confidence))
    )
    avg_conf = avg_confidence.scalar() or 0
    
    # أفضل الإشارات حسب الثقة
    top_signals_result = await db.execute(
        select(Signal)
        .where(Signal.signal_type != "NO_TRADE")
        .order_by(desc(Signal.confidence))
        .limit(10)
    )
    top_signals = [
        {
            "id": s.id,
            "symbol": s.symbol,
            "type": s.signal_type,
            "confidence": s.confidence,
            "created_at": s.created_at
        }
        for s in top_signals_result.scalars().all()
    ]
    
    return {
        "by_type": by_type,
        "by_status": by_status,
        "by_symbol": by_symbol,
        "average_confidence": round(float(avg_conf), 1),
        "top_signals": top_signals
    }


@router.get("/webhooks", response_model=List[dict])
async def get_webhook_logs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على سجلات Webhook
    """
    query = select(WebhookLog).order_by(desc(WebhookLog.created_at)).limit(limit).offset(skip)
    
    if status:
        query = query.where(WebhookLog.status == status)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "provider": log.provider,
            "event_type": log.event_type,
            "signal_id": log.signal_id,
            "status": log.status,
            "error_message": log.error_message,
            "created_at": log.created_at
        }
        for log in logs
    ]


@router.get("/subscriptions")
async def get_all_subscriptions(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على جميع الاشتراكات
    """
    query = select(Subscription).order_by(desc(Subscription.start_date)).limit(limit).offset(skip)
    
    if status:
        query = query.where(Subscription.status == status)
    
    result = await db.execute(query)
    subs = result.scalars().all()
    
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "tier": s.tier,
            "status": s.status,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "auto_renew": s.auto_renew,
            "payment_method": s.payment_method
        }
        for s in subs
    ]


@router.get("/payments")
async def get_payment_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على سجل المدفوعات
    """
    result = await db.execute(
        select(PaymentHistory)
        .order_by(desc(PaymentHistory.created_at))
        .limit(limit)
        .offset(skip)
    )
    payments = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "amount": p.amount,
            "currency": p.currency,
            "payment_method": p.payment_method,
            "status": p.status,
            "tier": p.tier,
            "created_at": p.created_at
        }
        for p in payments
    ]


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    تعطيل مستخدم
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user.is_active = False
    await db.commit()
    
    return {"message": "تم تعطيل المستخدم بنجاح"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    تفعيل مستخدم
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user.is_active = True
    await db.commit()
    
    return {"message": "تم تفعيل المستخدم بنجاح"}


@router.delete("/signals/{signal_id}")
async def delete_signal(
    signal_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    حذف إشارة
    """
    result = await db.execute(select(Signal).where(Signal.id == signal_id))
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الإشارة غير موجودة"
        )
    
    await db.delete(signal)
    await db.commit()
    
    return {"message": "تم حذف الإشارة بنجاح"}