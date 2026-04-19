"""
مسارات الاشتراكات - إدارة خطط الاشتراك والترقيات
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Subscription
from ..schemas import (
    SubscriptionPlanResponse,
    SubscriptionResponse,
    SubscribeRequest,
    SubscriptionStatsResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["الاشتراكات"])


# تعريف خطط الاشتراك
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "مجاني",
        "name_ar": "مجاني",
        "price": 0,
        "price_monthly": 0,
        "period_days": None,
        "features": [
            "إشارة واحدة يومياً",
            "الذهب فقط (XAUUSD)",
            "إطار زمني واحد",
            "دعم أساسي",
            "إشارات بدون تاريخ"
        ],
        "limits": {
            "signals_per_day": 1,
            "symbols": ["XAUUSD"],
            "timeframes": ["1h"],
            "history_days": 0
        }
    },
    "pro": {
        "name": "Pro",
        "name_ar": "احترافي",
        "price": 49.99,
        "price_monthly": 49.99,
        "period_days": 30,
        "features": [
            "إشارات غير محدودة",
            "جميع أزواج العملات",
            "4 أطر زمنية",
            "دعم متقدم",
            "سجل 30 يوم",
            "إشعارات Telegram",
            "تحليل يومي"
        ],
        "limits": {
            "signals_per_day": -1,  # غير محدود
            "symbols": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"],
            "timeframes": ["15min", "30min", "1h", "4h"],
            "history_days": 30
        }
    },
    "vip": {
        "name": "VIP",
        "name_ar": "مميز",
        "price": 99.99,
        "price_monthly": 99.99,
        "period_days": 30,
        "features": [
            "كل شيء في Pro",
            "جميع الأدوات بما فيها العملات المشفرة",
            "جميع الأطر الزمنية",
            "دعم VIP مخصص",
            "سجل غير محدود",
            "إشارات VIP حصرية",
            "توصيات يدوية يومية",
            "تحليلات متقدمة"
        ],
        "limits": {
            "signals_per_day": -1,
            "symbols": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "BTCUSD", "ETHUSD"],
            "timeframes": ["5min", "15min", "30min", "1h", "4h", "1day"],
            "history_days": -1  # غير محدود
        }
    }
}


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans():
    """
    الحصول على جميع خطط الاشتراك المتاحة
    """
    plans = []
    for tier, data in SUBSCRIPTION_PLANS.items():
        plans.append(SubscriptionPlanResponse(
            tier=tier,
            name=data["name"],
            name_ar=data["name_ar"],
            price=data["price"],
            price_monthly=data["price_monthly"],
            period_days=data["period_days"],
            features=data["features"],
            limits=data["limits"]
        ))
    return plans


@router.get("/plans/{tier}", response_model=SubscriptionPlanResponse)
async def get_plan_details(tier: str):
    """
    الحصول على تفاصيل خطة اشتراك محددة
    """
    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخطة غير موجودة"
        )
    
    data = SUBSCRIPTION_PLANS[tier]
    return SubscriptionPlanResponse(
        tier=tier,
        name=data["name"],
        name_ar=data["name_ar"],
        price=data["price"],
        price_monthly=data["price_monthly"],
        period_days=data["period_days"],
        features=data["features"],
        limits=data["limits"]
    )


@router.get("/my", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على معلومات اشتراك المستخدم الحالي
    """
    # البحث عن الاشتراك النشط
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).order_by(desc(Subscription.start_date))
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # المستخدم ليس لديه اشتراك نشط
        return SubscriptionResponse(
            tier="free",
            name="مجاني",
            name_ar="مجاني",
            status="active",
            start_date=current_user.created_at,
            end_date=None,
            features=SUBSCRIPTION_PLANS["free"]["features"],
            days_remaining=None,
            auto_renew=False
        )
    
    # حساب الأيام المتبقية
    days_remaining = None
    if subscription.end_date:
        remaining = subscription.end_date - datetime.utcnow()
        days_remaining = max(0, remaining.days)
    
    plan_data = SUBSCRIPTION_PLANS.get(subscription.tier, SUBSCRIPTION_PLANS["free"])
    
    return SubscriptionResponse(
        tier=subscription.tier,
        name=plan_data["name"],
        name_ar=plan_data["name_ar"],
        status=subscription.status,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        features=plan_data["features"],
        days_remaining=days_remaining,
        auto_renew=subscription.auto_renew
    )


@router.post("/subscribe")
async def subscribe_to_plan(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الاشتراك في خطة جديدة
    
    ملاحظة: في التطبيق الفعلي، سيتم الاتصال ببوابة الدفع
    """
    if request.tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الخطة غير صالحة"
        )
    
    # التحقق من وجود اشتراك نشط
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    active_subscription = result.scalar_one_or_none()
    
    if active_subscription:
        # تحديث الاشتراك الموجود
        active_subscription.status = "cancelled"
        active_subscription.cancelled_at = datetime.utcnow()
    
    plan_data = SUBSCRIPTION_PLANS[request.tier]
    
    # إنشاء اشتراك جديد
    start_date = datetime.utcnow()
    end_date = None
    if plan_data["period_days"]:
        end_date = start_date + timedelta(days=plan_data["period_days"])
    
    new_subscription = Subscription(
        user_id=current_user.id,
        tier=request.tier,
        status="active",
        start_date=start_date,
        end_date=end_date,
        auto_renew=request.auto_renew,
        payment_method=request.payment_method or "mock"
    )
    
    db.add(new_subscription)
    
    # تحديث مستوى الاشتراك في جدول المستخدمين
    current_user.subscription_tier = request.tier
    current_user.subscription_end = end_date
    
    await db.commit()
    
    return {
        "message": "تم الاشتراك بنجاح",
        "tier": request.tier,
        "start_date": start_date,
        "end_date": end_date
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    إلغاء الاشتراك
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لا يوجد اشتراك نشط لإلغائه"
        )
    
    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.utcnow()
    subscription.auto_renew = False
    
    # إعادة المستخدم للخطة المجانية
    current_user.subscription_tier = "free"
    
    await db.commit()
    
    return {"message": "تم إلغاء الاشتراك بنجاح"}


@router.post("/renew")
async def renew_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تجديد الاشتراك
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لا يوجد اشتراك نشط لتجديده"
        )
    
    plan_data = SUBSCRIPTION_PLANS.get(subscription.tier)
    if not plan_data or not plan_data["period_days"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن تجديد هذه الخطة"
        )
    
    # تحديث تاريخ الانتهاء
    if subscription.end_date:
        new_end = subscription.end_date + timedelta(days=plan_data["period_days"])
    else:
        new_end = datetime.utcnow() + timedelta(days=plan_data["period_days"])
    
    subscription.end_date = new_end
    
    await db.commit()
    
    return {
        "message": "تم تجديد الاشتراك بنجاح",
        "new_end_date": new_end
    }


@router.get("/stats", response_model=SubscriptionStatsResponse)
async def get_subscription_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على إحصائيات الاشتراك
    """
    # الحصول على الاشتراك الحالي
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        plan_data = SUBSCRIPTION_PLANS["free"]
        return SubscriptionStatsResponse(
            current_tier="free",
            days_remaining=None,
            total_signals_used=0,
            signals_limit=plan_data["limits"]["signals_per_day"],
            limit_type="daily" if plan_data["limits"]["signals_per_day"] > 0 else "unlimited"
        )
    
    plan_data = SUBSCRIPTION_PLANS.get(subscription.tier, SUBSCRIPTION_PLANS["free"])
    days_remaining = 0
    if subscription.end_date:
        remaining = subscription.end_date - datetime.utcnow()
        days_remaining = max(0, remaining.days)
    
    # حساب عدد الإشارات المستخدمة (محاكاة)
    signals_used_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    signals_count = signals_used_result.scalars().count()
    
    return SubscriptionStatsResponse(
        current_tier=subscription.tier,
        days_remaining=days_remaining,
        total_signals_used=signals_count,
        signals_limit=plan_data["limits"]["signals_per_day"],
        limit_type="daily" if plan_data["limits"]["signals_per_day"] > 0 else "unlimited"
    )


@router.get("/history")
async def get_payment_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على سجل المدفوعات
    """
    result = await db.execute(
        select(PaymentHistory)
        .where(PaymentHistory.user_id == current_user.id)
        .order_by(desc(PaymentHistory.created_at))
        .limit(limit)
    )
    payments = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "amount": p.amount,
            "currency": p.currency,
            "payment_method": p.payment_method,
            "status": p.status,
            "tier": p.tier,
            "created_at": p.created_at
        }
        for p in payments
    ]


def check_feature_access(user: User, feature: str) -> bool:
    """
    التحقق من صلاحية المستخدم للوصول لميزة معينة
    
    Args:
        user: المستخدم
        feature: اسم الميزة
    
    Returns:
        True إذا كان لديه صلاحية، False otherwise
    """
    tier = user.subscription_tier or "free"
    plan_data = SUBSCRIPTION_PLANS.get(tier, SUBSCRIPTION_PLANS["free"])
    
    # المميزات المسموحة للخطة المجانية
    free_features = ["basic_signals", "dashboard", "calculator"]
    
    # المميزات المسموحة للخطة الاحترافية
    pro_features = free_features + ["pro_signals", "telegram_alerts", "daily_analysis"]
    
    # المميزات المسموحة للخطة المميزة
    vip_features = pro_features + ["vip_signals", "manual_signals", "advanced_analytics"]
    
    tier_features = {
        "free": free_features,
        "pro": pro_features,
        "vip": vip_features
    }
    
    features = tier_features.get(tier, free_features)
    return feature in features