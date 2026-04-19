"""
مسارات Webhook - استقبال إشعارات TradingView ومعالجتها
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, Dict, Any
from datetime import datetime
import hmac
import hashlib

from ..database import get_db
from ..models import User, Signal, WebhookLog
from ..schemas import TradingViewWebhookPayload, WebhookResponse
from ..services.market_data import market_data_service
from ..services.signal_service import enhanced_signal_generator
from .auth import get_current_user

router = APIRouter(prefix="/webhook", tags=["Webhook"])


def verify_tradingview_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    التحقق من توقيع TradingView
    
    Args:
        payload: البيانات الخام للطلب
        signature: التوقيع من TradingView
        secret: السر المشترك
    
    Returns:
        True إذا كان التوقيع صحيحاً، False otherwise
    """
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


async def validate_webhook_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    التحقق من صحة بيانات Webhook من TradingView
    
    Args:
        data: بيانات الـ payload
    
    Returns:
        البيانات validate أو خطأ
    """
    errors = []
    
    # التحقق من الرمز
    if "symbol" not in data or not data["symbol"]:
        errors.append("الرمز مطلوب")
    elif data["symbol"] not in ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD"]:
        errors.append(f"الرمز {data['symbol']} غير مدعوم")
    
    # التحقق من السعر
    if "price" not in data or not data["price"]:
        errors.append("السعر مطلوب")
    else:
        try:
            float(data["price"])
        except ValueError:
            errors.append("السعر يجب أن يكون رقماً")
    
    # التحقق من نوع المشغل
    if "trigger" not in data or data["trigger"] not in ["Buy", "Sell", "Long", "Short", "alert"]:
        errors.append("نوع المشغل غير صالح")
    
    if errors:
        raise ValueError(" | ".join(errors))
    
    return data


async def run_internal_validation(
    symbol: str,
    timeframe: str,
    trigger_type: str,
    price: float
) -> Dict[str, Any]:
    """
    إعادة تشغيل التحقق من الإشارة داخلياً قبل الحفظ
    
    Args:
        symbol: رمز السوق
        timeframe: الإطار الزمني
        trigger_type: نوع المشغل (Buy/Sell)
        price: السعر الحالي
    
    Returns:
        نتيجة التحقق الداخلي
    """
    try:
        # جلب البيانات التاريخية
        candles = await market_data_service.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=200
        )
        
        if not candles or len(candles) < 100:
            return {
                "is_valid": False,
                "reason": "لا توجد بيانات كافية للتحقق الداخلي"
            }
        
        # توليد إشارة داخلية للمقارنة
        internal_signal = signal_generator.analyze(
            candles=candles,
            balance=10000,  # رصيد افتراضي للتحقق
            risk_percent=2  # نسبة مخاطر افتراضية
        )
        
        # مقارنة النتيجة
        # إذا كانت الإشارة الداخلية متوافقة مع إشارة TradingView
        if internal_signal.signal_type == "NO_TRADE":
            return {
                "is_valid": False,
                "reason": "التحقق الداخلي أظهر عدم وجود إشارة قوية",
                "confidence": internal_signal.confidence
            }
        
        # التحقق من اتجاه الإشارة
        trigger_to_signal = {
            "Buy": "BUY",
            "Long": "BUY",
            "Sell": "SELL",
            "Short": "SELL"
        }
        
        expected_signal = trigger_to_signal.get(trigger_type)
        
        if internal_signal.signal_type != expected_signal:
            return {
                "is_valid": False,
                "reason": f"عدم توافق: TradingView أظهر {trigger_type} لكن التحليل الداخلي أظهر {internal_signal.signal_type}",
                "confidence": internal_signal.confidence,
                "internal_signal": internal_signal.signal_type
            }
        
        # التحقق من مستوى السعر
        price_diff = abs(internal_signal.entry_price - price) / price * 100
        
        if price_diff > 1:  # أكثر من 1% فرق
            return {
                "is_valid": False,
                "reason": f"فرق كبير في السعر: {price_diff:.2f}%",
                "confidence": internal_signal.confidence
            }
        
        return {
            "is_valid": True,
            "confidence": internal_signal.confidence,
            "internal_signal": internal_signal.signal_type,
            "entry_price": internal_signal.entry_price,
            "stop_loss": internal_signal.stop_loss,
            "take_profit_1": internal_signal.take_profit_1,
            "take_profit_2": internal_signal.take_profit_2
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"خطأ في التحقق الداخلي: {str(e)}"
        }


@router.post("/tradingview", response_model=WebhookResponse)
async def receive_tradingview_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    استقبال webhook من TradingView
    
    هذه النقطة تستقبل الإشعارات من TradingView Alert وتقوم بـ:
    1. التحقق من صحة البيانات
    2. التحقق داخلياً من الإشارة
    3. حفظ الإشارة الصالحة في قاعدة البيانات
    
    Body Payload:
    ```json
    {
        "symbol": "XAUUSD",
        "timeframe": "1h",
        "trigger": "Buy",
        "price": 2350.50,
        "volume": 1500,
        "bar_time": "2024-01-15T10:00:00",
        "text": "Buy signal on XAUUSD"
    }
    ```
    """
    # قراءة البيانات الخام
    raw_body = await request.body()
    
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="بيانات JSON غير صالحة"
        )
    
    # تسجيل الطلب في السجل
    webhook_log = WebhookLog(
        provider="tradingview",
        event_type=data.get("trigger", "unknown"),
        payload=data,
        status="received"
    )
    db.add(webhook_log)
    await db.commit()
    
    # التحقق من صحة البيانات
    try:
        validated_data = await validate_webhook_payload(data)
    except ValueError as e:
        webhook_log.status = "validation_failed"
        webhook_log.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # استخراج البيانات
    symbol = validated_data["symbol"]
    timeframe = validated_data.get("timeframe", "1h")
    trigger_type = validated_data["trigger"]
    price = float(validated_data["price"])
    
    # التحقق داخلياً
    validation_result = await run_internal_validation(
        symbol=symbol,
        timeframe=timeframe,
        trigger_type=trigger_type,
        price=price
    )
    
    webhook_log.validation_result = validation_result
    
    if not validation_result.get("is_valid"):
        webhook_log.status = "validation_failed"
        await db.commit()
        
        return WebhookResponse(
            success=False,
            message=validation_result.get("reason", "فشل التحقق الداخلي"),
            signal_id=None,
            confidence=validation_result.get("confidence", 0)
        )
    
    # البحث عن المستخدم الافتراضي أو إنشاء إشارة عامة
    # في التطبيق الفعلي، يجب ربط Webhook بحساب مستخدم معين
    result = await db.execute(
        select(User).where(User.is_admin == True).limit(1)
    )
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        # إنشاء مستخدم افتراضي للإشارات العامة
        from ..core.security import hash_password
        admin_user = User(
            email="system@forexai.local",
            hashed_password=hash_password("webhook_internal_key"),
            full_name="نظام الإشارات",
            subscription_tier="vip",
            is_admin=True
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
    
    # تحديد نوع الإشارة
    signal_mapping = {
        "Buy": "BUY",
        "Long": "BUY",
        "Sell": "SELL",
        "Short": "SELL"
    }
    signal_type = signal_mapping.get(trigger_type, "BUY")
    
    # إنشاء الإشارة
    new_signal = Signal(
        user_id=admin_user.id,
        symbol=symbol,
        signal_type=signal_type,
        entry_price=price,
        stop_loss=validation_result.get("stop_loss", price * 0.995),
        take_profit_1=validation_result.get("take_profit_1", price * 1.015),
        take_profit_2=validation_result.get("take_profit_2", price * 1.025),
        lot_size=0.1,  # حجم افتراضي
        confidence=validation_result.get("confidence", 50),
        timeframe=timeframe,
        status="pending",
        explanation=f"إشارة من TradingView: {data.get('text', 'بدون وصف')}\n"
                    f"التحقق الداخلي:_signal_confirmed",
        source="tradingview",
        indicators_data={
            "trigger_price": price,
            "trigger_type": trigger_type,
            "validation": validation_result
        }
    )
    
    db.add(new_signal)
    await db.commit()
    await db.refresh(new_signal)
    
    webhook_log.signal_id = new_signal.id
    webhook_log.status = "success"
    await db.commit()
    
    return WebhookResponse(
        success=True,
        message="تم استقبال وتأكيد الإشارة بنجاح",
        signal_id=new_signal.id,
        confidence=new_signal.confidence
    )


@router.get("/logs")
async def get_webhook_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على سجل Webhooks
    (يتطلب صلاحيات المشرف)
    """
    # التحقق من صلاحيات المشرف
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح بالوصول"
        )
    
    result = await db.execute(
        select(WebhookLog)
        .order_by(desc(WebhookLog.created_at))
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "provider": log.provider,
            "event_type": log.event_type,
            "signal_id": log.signal_id,
            "status": log.status,
            "error_message": log.error_message,
            "validation_result": log.validation_result,
            "created_at": log.created_at
        }
        for log in logs
    ]


@router.delete("/logs/{log_id}")
async def delete_webhook_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    حذف سجل webhook
    (يتطلب صلاحيات المشرف)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح بالوصول"
        )
    
    result = await db.execute(
        select(WebhookLog).where(WebhookLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="السجل غير موجود"
        )
    
    await db.delete(log)
    await db.commit()
    
    return {"message": "تم حذف السجل بنجاح"}


@router.post("/test")
async def test_webhook(
    data: TradingViewWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    اختبار endpoint الـ webhook بدون حفظ
    """
    try:
        validated = await validate_webhook_payload(data.model_dump())
        validation_result = await run_internal_validation(
            symbol=validated["symbol"],
            timeframe=validated.get("timeframe", "1h"),
            trigger_type=validated["trigger"],
            price=float(validated["price"])
        )
        
        return {
            "validation": {
                "is_valid": validation_result.get("is_valid", False),
                "reason": validation_result.get("reason", "")
            },
            "data": validated,
            "confidence": validation_result.get("confidence", 0)
        }
        
    except ValueError as e:
        return {
            "validation": {
                "is_valid": False,
                "reason": str(e)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# نموذج payload لـ TradingView
TRADINGVIEW_WEBHOOK_EXAMPLE = {
    "symbol": "XAUUSD",
    "timeframe": "1h",
    "trigger": "Buy",
    "price": 2350.50,
    "volume": 1500,
    "bar_time": "2024-01-15T10:00:00",
    "text": "Buy signal on XAUUSD - Golden cross detected"
}