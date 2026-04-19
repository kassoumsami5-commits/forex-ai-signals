"""
خدمة حساب حجم اللوت - منطق حساب حجم الصفقة الأمثل
يدعم حسابات مختلفة للForex والذهب والمعادن
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LotCalculationResult:
    """نتيجة حساب حجم اللوت"""
    lot_size: float
    risk_amount: float
    pip_value: float
    stop_loss_pips: float
    message: str


class LotCalculator:
    """
    حاسبة حجم اللوت للتحكم في المخاطر
    
    تدعم:
    - أزواج العملات Forex
    - الذهب (XAUUSD)
    - المعادن الأخرى
    
    الحساب يعتمد على:
    - رصيد الحساب
    - نسبة المخاطر %
    - مسافة وقف الخسارة (بالنقاط)
    """
    
    # قيم النقاط (Pip) للأدوات المختلفة
    PIP_VALUES = {
        # أزواج العملات (تنسيق القائمة: [نقاط صغيرة, نقاط كبيرة])
        "EURUSD": [0.0001, 0.0001],
        "GBPUSD": [0.0001, 0.0001],
        "USDJPY": [0.01, 0.01],
        "USDCHF": [0.0001, 0.0001],
        "AUDUSD": [0.0001, 0.0001],
        "USDCAD": [0.0001, 0.0001],
        "NZDUSD": [0.0001, 0.0001],
        
        # المعادن النفيسة
        "XAUUSD": [0.01, 0.01],  # الذهب - النقطة = 0.01
        "XAGUSD": [0.01, 0.01],  # الفضة - النقطة = 0.01
        
        # العملات المشفرة (تقريبي)
        "BTCUSD": [0.1, 0.1],
        "ETHUSD": [0.01, 0.01],
    }
    
    # حجم اللوت القياسي لكل نوع من الأدوات
    STANDARD_LOT_SIZE = {
        "forex": 100000,  # 100,000 وحدة = 1 لوت قياسي
        "gold": 100,       # 100 أونصة = 1 لوت قياسي للذهب
        "crypto": 1,       # 1 وحدة = 1 لوت قياسي
    }
    
    @classmethod
    def get_pip_value(cls, symbol: str) -> float:
        """
        الحصول على قيمة النقطة للرمز
        
        Args:
            symbol: رمز السوق
        
        Returns:
            قيمة النقطة بالنقاط العشرية
        """
        if symbol in cls.PIP_VALUES:
            return cls.PIP_VALUES[symbol][0]
        
        # افتراضياً للـ Forex
        return 0.0001
    
    @classmethod
    def get_lot_type(cls, symbol: str) -> str:
        """
        تحديد نوع الأداة لحساب حجم اللوت
        
        Args:
            symbol: رمز السوق
        
        Returns:
            نوع الأداة: "forex", "gold", "crypto"
        """
        if symbol in ["XAUUSD", "XAGUSD"]:
            return "gold"
        elif symbol in ["BTCUSD", "ETHUSD"]:
            return "crypto"
        return "forex"
    
    @classmethod
    def calculate_lot_size(
        cls,
        balance: float,
        risk_percent: float,
        stop_loss_pips: float,
        symbol: str,
        account_currency: str = "USD"
    ) -> LotCalculationResult:
        """
        حساب حجم اللوت الأمثل
        
        المعادلة:
        حجم اللوت = (رأس المال × نسبة المخاطر) / (مسافة وقف الخسارة × قيمة النقطة × حجم اللوت القياسي)
        
        Args:
            balance: رصيد الحساب
            risk_percent: نسبة المخاطر % (مثال: 2 للـ 2%)
            stop_loss_pips: مسافة وقف الخسارة بالنقاط
            symbol: رمز السوق
            account_currency: عملة الحساب
        
        Returns:
            LotCalculationResult مع حجم اللوت والبيانات ذات الصلة
        """
        if balance <= 0:
            return LotCalculationResult(
                lot_size=0.0,
                risk_amount=0.0,
                pip_value=0.0,
                stop_loss_pips=stop_loss_pips,
                message="خطأ: الرصيد يجب أن يكون أكبر من صفر"
            )
        
        if risk_percent <= 0 or risk_percent > 100:
            return LotCalculationResult(
                lot_size=0.0,
                risk_amount=0.0,
                pip_value=0.0,
                stop_loss_pips=stop_loss_pips,
                message="خطأ: نسبة المخاطر يجب أن تكون بين 0.1 و 100"
            )
        
        if stop_loss_pips <= 0:
            return LotCalculationResult(
                lot_size=0.0,
                risk_amount=0.0,
                pip_value=0.0,
                stop_loss_pips=stop_loss_pips,
                message="خطأ: مسافة وقف الخسارة يجب أن تكون أكبر من صفر"
            )
        
        # حساب مبلغ المخاطر
        risk_amount = balance * (risk_percent / 100)
        
        # الحصول على قيمة النقطة
        pip_value = cls.get_pip_value(symbol)
        
        # الحصول على نوع الأداة
        lot_type = cls.get_lot_type(symbol)
        
        # حجم اللوت القياسي
        standard_lot = cls.STANDARD_LOT_SIZE.get(lot_type, 100000)
        
        # حساب حجم اللوت
        if lot_type == "forex":
            # للـ Forex: اللوت = المخاطر / (النقاط × قيمة النقطة × حجم اللوت)
            # أولاً: قيمة النقطة بالدولار = النقطة × حجم اللوت القياسي × سعر الصرف
            pip_value_usd = pip_value * standard_lot
            
            # حساب حجم اللوت
            lot_size = risk_amount / (stop_loss_pips * pip_value_usd)
            
        elif lot_type == "gold":
            # للذهب: اللوت = المخاطر / (النقاط × قيمة النقطة × حجم اللوت)
            # قيمة النقطة للذهب = 0.01 × 100 = 1 دولار لكل لوت
            pip_value_usd = pip_value * standard_lot
            
            lot_size = risk_amount / (stop_loss_pips * pip_value_usd)
            
        else:
            # للعملات المشفرة أو الأدوات الأخرى
            pip_value_usd = pip_value * standard_lot
            lot_size = risk_amount / (stop_loss_pips * pip_value_usd)
        
        # تقريب حجم اللوت
        # للـ Forex: أقرب 0.01
        # للذهب: أقرب 0.01
        # للعملات المشفرة: أقرب 0.001
        if lot_type == "crypto":
            lot_size = round(lot_size, 4)
        else:
            lot_size = round(lot_size, 2)
        
        # التحقق من الحد الأدنى والأقصى
        min_lot = 0.01
        max_lot = 100.0
        
        if lot_size < min_lot:
            return LotCalculationResult(
                lot_size=min_lot,
                risk_amount=risk_amount,
                pip_value=pip_value,
                stop_loss_pips=stop_loss_pips,
                message=f"حجم اللوت أقل من الحد الأدنى. تم تعيينه إلى {min_lot}"
            )
        
        if lot_size > max_lot:
            return LotCalculationResult(
                lot_size=max_lot,
                risk_amount=risk_amount,
                pip_value=pip_value,
                stop_loss_pips=stop_loss_pips,
                message=f"حجم اللوت أعلى من الحد الأقصى. تم تعيينه إلى {max_lot}"
            )
        
        return LotCalculationResult(
            lot_size=lot_size,
            risk_amount=round(risk_amount, 2),
            pip_value=pip_value,
            stop_loss_pips=stop_loss_pips,
            message="تم حساب حجم اللوت بنجاح"
        )
    
    @classmethod
    def calculate_from_price_difference(
        cls,
        balance: float,
        risk_percent: float,
        entry_price: float,
        stop_loss_price: float,
        symbol: str
    ) -> Dict[str, Any]:
        """
        حساب حجم اللوت بناءً على فرق السعر الفعلي
        
        مفيد عندما يكون لديك سعر الدخول وسعر وقف الخسارة مباشرة
        
        Args:
            balance: رصيد الحساب
            risk_percent: نسبة المخاطر %
            entry_price: سعر الدخول
            stop_loss_price: سعر وقف الخسارة
            symbol: رمز السوق
        
        Returns:
            قاموس يحتوي على حجم اللوت والبيانات ذات الصلة
        """
        # حساب الفرق بالنقاط
        pip_value = cls.get_pip_value(symbol)
        price_difference = abs(entry_price - stop_loss_price)
        stop_loss_pips = price_difference / pip_value
        
        # حساب حجم اللوت
        result = cls.calculate_lot_size(
            balance=balance,
            risk_percent=risk_percent,
            stop_loss_pips=stop_loss_pips,
            symbol=symbol
        )
        
        return {
            "lot_size": result.lot_size,
            "risk_amount": result.risk_amount,
            "stop_loss_pips": result.stop_loss_pips,
            "pip_value": result.pip_value,
            "price_difference": round(price_difference, 5),
            "message": result.message
        }
    
    @classmethod
    def validate_risk_amount(
        cls,
        balance: float,
        risk_percent: float,
        expected_risk: float
    ) -> Dict[str, Any]:
        """
        التحقق من مبلغ المخاطر المتوقع
        
        Args:
            balance: رصيد الحساب
            risk_percent: نسبة المخاطر %
            expected_risk: مبلغ المخاطر المتوقع
        
        Returns:
            قاموس يحتوي على نتيجة التحقق
        """
        calculated_risk = balance * (risk_percent / 100)
        
        is_valid = abs(calculated_risk - expected_risk) < 0.01
        
        return {
            "is_valid": is_valid,
            "calculated_risk": round(calculated_risk, 2),
            "expected_risk": round(expected_risk, 2),
            "difference": round(abs(calculated_risk - expected_risk), 2),
            "message": "مبلغ المخاطر متطابق" if is_valid else "مبلغ المخاطر غير متطابق"
        }


# إنشاء مثيل عام للحاسبة
lot_calculator = LotCalculator()