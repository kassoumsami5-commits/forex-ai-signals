"""
محرك توليد الإشارات - نظام التحليل الفني المتقدم والمحسن
يدعم الذهب (XAUUSD) وأزواج العملات مع تحليلConditions متقدمة
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime


class MarketCondition(Enum):
    """ظروف السوق"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"


class SignalQuality(Enum):
    """جودة الإشارة"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    REJECTED = "REJECTED"


@dataclass
class SignalResult:
    """نتيجة تحليل الإشارة المحسنة"""
    signal_type: str  # BUY, SELL, NO_TRADE
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    lot_size: float
    confidence: float  # 0-100%
    explanation: str  # تفسير كامل بالعربية
    indicators: Dict[str, Any]
    trend: str
    market_condition: str  # ظروف السوق
    signal_quality: str  # جودة الإشارة
    risk_reward_ratio: float  # نسبة المخاطرة/المكافأة
    warning_messages: List[str] = field(default_factory=list)
    timestamp: str = ""


class AdvancedTechnicalIndicators:
    """مؤشرات فنية متقدمة"""
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """حساب EMA مع معالجة محسنة"""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(data[:period]) / period]
        
        for price in data[period:]:
            ema_value = (price - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)
        
        return ema
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        """حساب SMA"""
        if len(data) < period:
            return []
        
        result = []
        for i in range(period - 1, len(data)):
            avg = sum(data[i - period + 1:i + 1]) / period
            result.append(avg)
        return result
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """حساب RSI محسن"""
        if len(prices) < period + 1:
            return []
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = []
        avg_losses = []
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        avg_gains.append(avg_gain)
        avg_losses.append(avg_loss)
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gains[-1] * (period - 1) + gains[i]) / period
            avg_loss = (avg_losses[-1] * (period - 1) + losses[i]) / period
            avg_gains.append(avg_gain)
            avg_losses.append(avg_loss)
        
        rsi_values = []
        for gain, loss in zip(avg_gains, avg_losses):
            if loss == 0:
                rsi_values.append(100)
            else:
                rs = gain / loss
                rsi_values.append(100 - (100 / (1 + rs)))
        
        return rsi_values
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """حساب MACD"""
        if len(prices) < slow + signal:
            return [], [], []
        
        ema_fast = AdvancedTechnicalIndicators.ema(prices, fast)
        ema_slow = AdvancedTechnicalIndicators.ema(prices, slow)
        
        diff = len(ema_fast) - len(ema_slow)
        if diff > 0:
            ema_fast = ema_fast[diff:]
        
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = AdvancedTechnicalIndicators.ema(macd_line, signal)
        
        macd_diff = len(macd_line) - len(signal_line)
        if macd_diff > 0:
            macd_line = macd_line[macd_diff:]
        
        histogram = [m - s for m, s in zip(macd_line, signal_line)]
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """حساب ATR"""
        if len(highs) < period + 1:
            return []
        
        tr_list = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i - 1])
            low_close = abs(lows[i] - closes[i - 1])
            tr = max(high_low, high_close, low_close)
            tr_list.append(tr)
        
        atr = [sum(tr_list[:period]) / period]
        for i in range(period, len(tr_list)):
            atr_value = (atr[-1] * (period - 1) + tr_list[i]) / period
            atr.append(atr_value)
        
        return atr
    
    @staticmethod
    def adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Tuple[List[float], List[float], List[float]]:
        """
        حساب ADX (Average Directional Index)
        يقيس قوة الاتجاه بغض النظر عن اتجاهه
        ADX > 25 = اتجاه قوي
        ADX < 20 = سوق جانبي
        """
        if len(highs) < period * 2:
            return [], [], []
        
        # حساب +DM و -DM
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i - 1]
            low_diff = lows[i - 1] - lows[i]
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0)
            
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0)
        
        # حساب ATR
        atr_values = AdvancedTechnicalIndicators.atr(highs, lows, closes, period)
        
        if len(atr_values) < period:
            return [], [], []
        
        # حساب المتوسطات المتحركة للإتجاه
        plus_dm_ema = AdvancedTechnicalIndicators.ema(plus_dm, period)
        minus_dm_ema = AdvancedTechnicalIndicators.ema(minus_dm, period)
        
        # حساب DI+
        di_plus = []
        for i in range(len(plus_dm_ema)):
            if atr_values[i] > 0:
                di_plus.append((plus_dm_ema[i] / atr_values[i]) * 100)
            else:
                di_plus.append(0)
        
        # حساب DI-
        di_minus = []
        for i in range(len(minus_dm_ema)):
            if atr_values[i] > 0:
                di_minus.append((minus_dm_ema[i] / atr_values[i]) * 100)
            else:
                di_minus.append(0)
        
        # حساب DX
        dx = []
        for i in range(len(di_plus)):
            di_sum = di_plus[i] + di_minus[i]
            if di_sum > 0:
                dx.append(abs(di_plus[i] - di_minus[i]) / di_sum * 100)
            else:
                dx.append(0)
        
        # حساب ADX
        adx_values = AdvancedTechnicalIndicators.ema(dx, period)
        
        return adx_values, di_plus, di_minus
    
    @staticmethod
    def stochastics(highs: List[float], lows: List[float], closes: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """حساب Stochastic Oscillator"""
        if len(highs) < k_period:
            return [], []
        
        k_values = []
        for i in range(k_period - 1, len(closes)):
            highest = max(highs[i - k_period + 1:i + 1])
            lowest = min(lows[i - k_period + 1:i + 1])
            
            if highest != lowest:
                k = ((closes[i] - lowest) / (highest - lowest)) * 100
            else:
                k = 50
            k_values.append(k)
        
        d_values = AdvancedTechnicalIndicators.ema(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def calculate_volatility(closes: List[float], period: int = 20) -> float:
        """حساب التقلب (Volatility)"""
        if len(closes) < period:
            return 0
        
        returns = np.diff(closes) / closes[:-1]
        volatility = np.std(returns[-period:]) * 100
        
        return volatility


class XAUUSDSpecificAnalyzer:
    """محلل خاص بالذهب XAUUSD"""
    
    # معايير خاصة بالذهب
    GOLD_PIP_VALUE = 0.01  # قيمة النقطة للذهب
    GOLD_LOT_SIZE = 100  # حجم اللوت القياسي للذهب (100 أونصة)
    
    # مستويات ATR المئوية المفضلة للذهب
    ATR_MULTIPLIERS = {
        "tight": 1.0,   # وقف خسارة ضيق
        "normal": 1.5,  # وقف خسارة عادي
        "wide": 2.5     # وقف خسارة واسع
    }
    
    # حدود RSI للذهب
    RSI_OVERBOUGHT = 75
    RSI_OVERSOLD = 25
    RSI_NEUTRAL_HIGH = 55
    RSI_NEUTRAL_LOW = 45
    
    @classmethod
    def get_atr_multiplier(cls, risk_tolerance: str = "normal") -> float:
        """الحصول على مضاعف ATR بناءً على تحمل المخاطر"""
        return cls.ATR_MULTIPLIERS.get(risk_tolerance, 1.5)
    
    @classmethod
    def calculate_gold_pip_value_usd(cls, lot_size: float = 1.0) -> float:
        """حساب قيمة النقطة بالدولار للذهب"""
        return cls.GOLD_PIP_VALUE * cls.GOLD_LOT_SIZE * lot_size


class MarketConditionDetector:
    """كاشف ظروف السوق"""
    
    def __init__(self):
        self.indicators = AdvancedTechnicalIndicators()
    
    def detect_condition(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        symbol: str = "XAUUSD"
    ) -> Tuple[MarketCondition, Dict[str, Any]]:
        """
        تحديد ظروف السوق الحالية
        
        Returns:
            (حالة السوق, تفاصيل التحليل)
        """
        if len(closes) < 50:
            return MarketCondition.UNKNOWN, {}
        
        # حساب ADX لقياس قوة الاتجاه
        adx, di_plus, di_minus = self.indicators.adx(highs, lows, closes, 14)
        
        # حساب التقلب
        volatility = self.indicators.calculate_volatility(closes, 20)
        
        # حساب EMA للفحص
        ema_20 = self.indicators.ema(closes, 20)
        ema_50 = self.indicators.ema(closes, 50)
        
        if not all([adx, ema_20, ema_50]):
            return MarketCondition.UNKNOWN, {}
        
        adx_value = adx[-1] if adx else 0
        current_price = closes[-1]
        ema20_val = ema_20[-1]
        ema50_val = ema_50[-1]
        
        details = {
            "adx": round(adx_value, 2),
            "volatility": round(volatility, 3),
            "trend_strength": "STRONG" if adx_value > 25 else "WEAK",
            "ema_alignment": self._get_ema_alignment(ema20_val, ema50_val, current_price)
        }
        
        # تحديد الحالة
        if adx_value < 20:
            # سوق جانبي (Ranging)
            details["condition_reason"] = "مؤشر ADX أقل من 20 - لا يوجد اتجاه واضح"
            return MarketCondition.RANGING, details
        
        if volatility > 1.5:
            # سوق متقلب
            details["condition_reason"] = f"التقلب مرتفع ({volatility:.2f}%)"
            return MarketCondition.VOLATILE, details
        
        if adx_value > 25:
            # سوق متجه
            if ema20_val > ema50_val:
                details["condition_reason"] = "اتجاه صاعد قوي - EMA20 فوق EMA50"
                return MarketCondition.TRENDING_UP, details
            else:
                details["condition_reason"] = "اتجاه هابط قوي - EMA20 تحت EMA50"
                return MarketCondition.TRENDING_DOWN, details
        
        # حالة غير محددة
        details["condition_reason"] = "ظروف سوق غير واضحة"
        return MarketCondition.UNKNOWN, details
    
    def _get_ema_alignment(self, ema20: float, ema50: float, price: float) -> str:
        """تحديد محاذاة EMAs"""
        if price > ema20 > ema50:
            return "BULLISH_ALIGNMENT"
        elif price < ema20 < ema50:
            return "BEARISH_ALIGNMENT"
        else:
            return "NO_ALIGNMENT"


class SignalQualityFilter:
    """فلتر جودة الإشارة"""
    
    # الحد الأدنى من置信度 للمتاجرة
    MIN_CONFIDENCE_THRESHOLD = 60  # 60% حد أدنى
    
    # أوزان المكونات للConfidence Score
    WEIGHTS = {
        "trend_alignment": 25,      # محاذاة الاتجاه
        "momentum": 20,             # الزخم
        "indicator_agreement": 15,   # اتفاق المؤشرات
        "sr_proximity": 15,          # قرب المستويات
        "adx_strength": 15,         # قوة ADX
        "rsi_zone": 10               # منطقة RSI
    }
    
    @classmethod
    def evaluate_signal_quality(
        cls,
        trend: str,
        momentum: str,
        signal_type: str,
        rsi: float,
        adx: float,
        sr_strength: str,
        indicators_agreement: float
    ) -> Tuple[float, SignalQuality, List[str]]:
        """
        تقييم جودة الإشارة وحسابConfidence Score
        
        Returns:
            (الدرجة, جودة الإشارة, التحذيرات)
        """
        if signal_type == "NO_TRADE":
            return 0, SignalQuality.REJECTED, ["لا إشارة ملائمة حالياً"]
        
        score = 0
        warnings = []
        details = []
        
        # 1. محاذاة الاتجاه (25 نقطة)
        if signal_type == "BUY" and trend == "BULLISH":
            score += cls.WEIGHTS["trend_alignment"]
            details.append(f"اتجاه صاعد متوافق مع إشارة الشراء (+{cls.WEIGHTS['trend_alignment']})")
        elif signal_type == "SELL" and trend == "BEARISH":
            score += cls.WEIGHTS["trend_alignment"]
            details.append(f"اتجاه هابط متوافق مع إشارة البيع (+{cls.WEIGHTS['trend_alignment']})")
        else:
            warnings.append(f"الاتجاه ({trend}) غير متوافق تماماً مع نوع الإشارة ({signal_type})")
            score += 5  # درجة جزئية
        
        # 2. الزخم (20 نقطة)
        if momentum == "BULLISH" and signal_type == "BUY":
            score += cls.WEIGHTS["momentum"]
            details.append(f"زخم إيجابي يدعم الشراء (+{cls.WEIGHTS['momentum']})")
        elif momentum == "BEARISH" and signal_type == "SELL":
            score += cls.WEIGHTS["momentum"]
            details.append(f"زخم سلبي يدعم البيع (+{cls.WEIGHTS['momentum']})")
        elif momentum == "NEUTRAL":
            warnings.append("الزخم محايد - انتظر تأكيداً أقوى")
            score += 5
        else:
            warnings.append(f"الزخم ({momentum}) يتعارض مع الإشارة")
        
        # 3. اتفاق المؤشرات (15 نقطة)
        agreement_score = min(indicators_agreement, 100) / 100 * cls.WEIGHTS["indicator_agreement"]
        score += agreement_score
        if agreement_score >= cls.WEIGHTS["indicator_agreement"] * 0.8:
            details.append(f"المؤشرات متفقة بشكل قوي (+{int(agreement_score)})")
        elif agreement_score < cls.WEIGHTS["indicator_agreement"] * 0.5:
            warnings.append("بعض المؤشرات غير متفقة")
        
        # 4. قوة مستويات S/R (15 نقطة)
        if sr_strength == "STRONG":
            score += cls.WEIGHTS["sr_proximity"]
            details.append(f"مستويات دعم/مقاومة قوية (+{cls.WEIGHTS['sr_proximity']})")
        elif sr_strength == "MEDIUM":
            score += 8
            details.append("مستويات متوسطة القوة (+8)")
        else:
            warnings.append("المستويات ضعيفة - قد تكون الإشارة غير موثوقة")
            score += 3
        
        # 5. قوة ADX (15 نقطة)
        if adx >= 30:
            score += cls.WEIGHTS["adx_strength"]
            details.append(f"اتجاه قوي جداً (ADX={adx:.1f}) (+{cls.WEIGHTS['adx_strength']})")
        elif adx >= 20:
            score += 8
            details.append(f"اتجاه متوسط (ADX={adx:.1f}) (+8)")
        else:
            warnings.append(f"اتجاه ضعيف (ADX={adx:.1f}) - سوق جانبي محتمل")
            score += 2
        
        # 6. منطقة RSI (10 نقاط)
        if signal_type == "BUY":
            if 30 < rsi < 45:  # منطقة ذروة بيع محتملة
                score += cls.WEIGHTS["rsi_zone"]
                details.append(f"RSI في منطقة تشبع بيع ({rsi:.1f}) - فرصة شراء (+{cls.WEIGHTS['rsi_zone']})")
            elif 45 <= rsi <= 55:
                score += 5
                details.append(f"RSI محايد ({rsi:.1f}) (+5)")
            elif rsi >= 70:
                warnings.append(f"RSI في منطقة ذروة شراء ({rsi:.1f}) - انتظار تصحيح")
                score -= 5
        elif signal_type == "SELL":
            if 55 < rsi < 70:  # منطقة ذروة شراء محتملة
                score += cls.WEIGHTS["rsi_zone"]
                details.append(f"RSI في منطقة تشبع شراء ({rsi:.1f}) - فرصة بيع (+{cls.WEIGHTS['rsi_zone']})")
            elif 45 <= rsi <= 55:
                score += 5
            elif rsi <= 30:
                warnings.append(f"RSI في منطقة ذروة بيع ({rsi:.1f}) - انتظار تصحيح")
                score -= 5
        
        # تحديد الجودة
        if score >= 75:
            quality = SignalQuality.HIGH
        elif score >= 50:
            quality = SignalQuality.MEDIUM
        else:
            quality = SignalQuality.LOW
        
        # تطبيق الحد الأدنى
        if score < cls.MIN_CONFIDENCE_THRESHOLD:
            quality = SignalQuality.REJECTED
            warnings.append(f"الدرجة ({score:.0f}) أقل من الحد الأدنى ({cls.MIN_CONFIDENCE_THRESHOLD})")
        
        # تحديد الحد الأقصى
        final_score = min(95, max(0, score))
        
        return final_score, quality, warnings


class SupportResistanceAnalyzer:
    """محلل مستويات الدعم والمقاومة"""
    
    @staticmethod
    def find_swing_points(highs: List[float], lows: List[float], lookback: int = 5) -> Dict[str, List]:
        """إيجاد نقاط التأرجح"""
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, len(highs) - lookback):
            # قمة
            if all(highs[i] >= highs[i - j] for j in range(1, lookback + 1)) and \
               all(highs[i] > highs[i + j] for j in range(1, lookback + 1)):
                swing_highs.append((i, highs[i]))
            
            # قاع
            if all(lows[i] <= lows[i - j] for j in range(1, lookback + 1)) and \
               all(lows[i] < lows[i + j] for j in range(1, lookback + 1)):
                swing_lows.append((i, lows[i]))
        
        return {"swing_highs": swing_highs, "swing_lows": swing_lows}
    
    @staticmethod
    def cluster_levels(levels: List[float], tolerance: float = 0.002) -> List[float]:
        """تجميع المستويات المتقاربة"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) < tolerance:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clustered.append(np.mean(current_cluster))
        return clustered
    
    @classmethod
    def find_levels(cls, highs: List[float], lows: List[float], tolerance: float = 0.002) -> Dict[str, List[float]]:
        """إيجاد مستويات الدعم والمقاومة المجمعة"""
        swings = cls.find_swing_points(highs, lows)
        
        resistance = cls.cluster_levels([h for _, h in swings["swing_highs"]], tolerance)
        support = cls.cluster_levels([l for _, l in swings["swing_lows"]], tolerance)
        
        return {
            "support_levels": sorted(support),
            "resistance_levels": sorted(resistance)
        }
    
    @classmethod
    def analyze_proximity(cls, current_price: float, support: List[float], resistance: List[float]) -> Dict[str, Any]:
        """تحليل قرب السعر من المستويات"""
        active_support = [s for s in support if s < current_price]
        active_resistance = [r for r in resistance if r > current_price]
        
        nearest_support = max(active_support, default=0)
        nearest_resistance = min(active_resistance, default=0)
        
        # حساب المسافات بالنسبة المئوية
        if nearest_support > 0:
            support_dist = abs(current_price - nearest_support) / current_price * 100
        else:
            support_dist = 100
        
        if nearest_resistance > 0:
            resistance_dist = abs(nearest_resistance - current_price) / current_price * 100
        else:
            resistance_dist = 100
        
        # تحديد القوة
        if support_dist < 0.5 and resistance_dist < 0.5:
            strength = "STRONG"
        elif support_dist < 1.5 or resistance_dist < 1.5:
            strength = "MEDIUM"
        else:
            strength = "WEAK"
        
        return {
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_distance_pct": round(support_dist, 2),
            "resistance_distance_pct": round(resistance_dist, 2),
            "strength": strength
        }


class EnhancedSignalGenerator:
    """محرك توليد الإشارات المحسن"""
    
    def __init__(self):
        self.indicators = AdvancedTechnicalIndicators()
        self.condition_detector = MarketConditionDetector()
        self.sr_analyzer = SupportResistanceAnalyzer()
        self.quality_filter = SignalQualityFilter()
        self.gold_analyzer = XAUUSDSpecificAnalyzer()
    
    def analyze(
        self,
        candles: List[Dict[str, Any]],
        balance: float,
        risk_percent: float,
        symbol: str = "XAUUSD"
    ) -> SignalResult:
        """
        تحليل شامل وتوليد إشارة trading
        
        Args:
            candles: بيانات الشموع التاريخية
            balance: رصيد الحساب
            risk_percent: نسبة المخاطر
            symbol: رمز السوق
        
        Returns:
            SignalResult مع تفاصيل الإشارة والتحليل
        """
        if len(candles) < 200:
            return self._no_trade_result(
                "لا توجد بيانات كافية للتحليل. تحتاج على الأقل 200 شمعة.",
                "UNKNOWN"
            )
        
        # استخراج البيانات
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]
        
        current_price = closes[-1]
        
        # 1. حساب جميع المؤشرات
        ema_20 = self.indicators.ema(closes, 20)
        ema_50 = self.indicators.ema(closes, 50)
        ema_200 = self.indicators.ema(closes, 200)
        rsi = self.indicators.rsi(closes, 14)
        macd_line, signal_line, histogram = self.indicators.macd(closes)
        atr = self.indicators.atr(highs, lows, closes, 14)
        adx, di_plus, di_minus = self.indicators.adx(highs, lows, closes, 14)
        stoch_k, stoch_d = self.indicators.stochastics(highs, lows, closes)
        
        # 2. تحديد ظروف السوق
        market_condition, condition_details = self.condition_detector.detect_condition(
            highs, lows, closes, symbol
        )
        
        # 3. تحليل مستويات S/R
        levels = self.sr_analyzer.find_levels(highs, lows)
        sr_analysis = self.sr_analyzer.analyze_proximity(
            current_price, 
            levels["support_levels"], 
            levels["resistance_levels"]
        )
        
        # 4. تحليل الاتجاه
        trend = self._analyze_trend(ema_20, ema_50, ema_200, current_price, adx)
        
        # 5. تحليل الزخم
        momentum = self._analyze_momentum(rsi, macd_line, signal_line, histogram, di_plus, di_minus)
        
        # 6. حساب اتفاق المؤشرات
        indicator_agreement = self._calculate_indicator_agreement(
            trend, momentum, rsi, macd_line, signal_line, adx, stoch_k, stoch_d
        )
        
        # 7. تقييم جودة الإشارة
        confidence, quality, warnings = self.quality_filter.evaluate_signal_quality(
            trend=trend,
            momentum=momentum,
            signal_type="",  # سيتم تحديده لاحقاً
            rsi=rsi[-1] if rsi else 50,
            adx=adx[-1] if adx else 0,
            sr_strength=sr_analysis["strength"],
            indicators_agreement=indicator_agreement
        )
        
        # 8. تحديد نوع الإشارة
        signal_type, entry_price, sl, tp1, tp2 = self._determine_signal(
            trend=trend,
            momentum=momentum,
            market_condition=market_condition,
            current_price=current_price,
            sr_analysis=sr_analysis,
            atr=atr,
            rsi=rsi
        )
        
        # 9. إعادة تقييم الجودة مع نوع الإشارة
        confidence, quality, warnings = self.quality_filter.evaluate_signal_quality(
            trend=trend,
            momentum=momentum,
            signal_type=signal_type,
            rsi=rsi[-1] if rsi else 50,
            adx=adx[-1] if adx else 0,
            sr_strength=sr_analysis["strength"],
            indicators_agreement=indicator_agreement
        )
        
        # 10. التحقق من الحد الأدنى للConfidence
        if quality == SignalQuality.REJECTED or confidence < 60:
            return self._no_trade_result(
                self._generate_rejection_reason(
                    trend, momentum, market_condition, confidence, warnings
                ),
                market_condition.value if market_condition else "UNKNOWN"
            )
        
        # 11. حساب حجم اللوت
        lot_size = self._calculate_lot_size(balance, risk_percent, entry_price, sl, symbol)
        
        # 12. حساب نسبة المخاطرة/المكافأة
        risk_reward = self._calculate_risk_reward(entry_price, sl, tp1)
        
        # 13. توليد التفسير الكامل بالعربية
        explanation = self._generate_comprehensive_explanation(
            signal_type=signal_type,
            trend=trend,
            momentum=momentum,
            market_condition=market_condition,
            rsi=rsi[-1] if rsi else 50,
            adx=adx[-1] if adx else 0,
            sr_analysis=sr_analysis,
            confidence=confidence,
            quality=quality,
            atr=atr[-1] if atr else 0,
            risk_reward=risk_reward
        )
        
        # إضافة التحذيرات للتوضيح
        all_warnings = warnings.copy()
        if market_condition == MarketCondition.RANGING:
            all_warnings.append("السوق في وضع جانبي - انتظر كسر المستويات")
        elif market_condition == MarketCondition.VOLATILE:
            all_warnings.append("السوق متقلب - استخدم وقف خسارة واسع")
        
        return SignalResult(
            signal_type=signal_type,
            entry_price=round(entry_price, 5),
            stop_loss=round(sl, 5),
            take_profit_1=round(tp1, 5),
            take_profit_2=round(tp2, 5),
            lot_size=round(lot_size, 2),
            confidence=round(confidence, 1),
            explanation=explanation,
            indicators={
                "ema_20": round(ema_20[-1], 5) if ema_20 else 0,
                "ema_50": round(ema_50[-1], 5) if ema_50 else 0,
                "ema_200": round(ema_200[-1], 5) if ema_200 else 0,
                "rsi": round(rsi[-1], 2) if rsi else 50,
                "macd": round(macd_line[-1], 5) if macd_line else 0,
                "macd_signal": round(signal_line[-1], 5) if signal_line else 0,
                "macd_histogram": round(histogram[-1], 5) if histogram else 0,
                "atr": round(atr[-1], 5) if atr else 0,
                "adx": round(adx[-1], 2) if adx else 0,
                "stoch_k": round(stoch_k[-1], 2) if stoch_k else 50,
                "stoch_d": round(stoch_d[-1], 2) if stoch_d else 50,
                "support_levels": levels["support_levels"][:5],
                "resistance_levels": levels["resistance_levels"][:5],
                "indicator_agreement_pct": indicator_agreement
            },
            trend=trend,
            market_condition=market_condition.value if market_condition else "UNKNOWN",
            signal_quality=quality.value if quality else "LOW",
            risk_reward_ratio=round(risk_reward, 2),
            warning_messages=all_warnings,
            timestamp=datetime.now().isoformat()
        )
    
    def _analyze_trend(
        self,
        ema_20: List[float],
        ema_50: List[float],
        ema_200: List[float],
        current_price: float,
        adx: List[float]
    ) -> str:
        """تحليل_direction مع مراعاة ADX"""
        if not all([ema_20, ema_50, ema_200]):
            return "NEUTRAL"
        
        e20 = ema_20[-1]
        e50 = ema_50[-1]
        e200 = ema_200[-1]
        
        adx_val = adx[-1] if adx else 0
        
        # شروط الاتجاه الصاعد القوي
        if current_price > e20 > e50 > e200 and adx_val > 20:
            return "BULLISH"
        # شروط الاتجاه الهابط القوي
        elif current_price < e20 < e50 < e200 and adx_val > 20:
            return "BEARISH"
        # شروط السوق الضعيف/جانبي
        else:
            return "NEUTRAL"
    
    def _analyze_momentum(
        self,
        rsi: List[float],
        macd_line: List[float],
        signal_line: List[float],
        histogram: List[float],
        di_plus: List[float],
        di_minus: List[float]
    ) -> str:
        """تحليل الزخم مع مؤشرات متعددة"""
        if not all([rsi, macd_line, signal_line]):
            return "NEUTRAL"
        
        rsi_val = rsi[-1]
        macd_val = macd_line[-1] if macd_line else 0
        sig_val = signal_line[-1] if signal_line else 0
        hist_val = histogram[-1] if histogram else 0
        
        di_p = di_plus[-1] if di_plus else 0
        di_m = di_minus[-1] if di_minus else 0
        
        bullish_count = 0
        bearish_count = 0
        
        # RSI
        if rsi_val > 60:
            bullish_count += 1
        elif rsi_val < 40:
            bearish_count += 1
        
        # MACD
        if macd_val > sig_val and hist_val > 0:
            bullish_count += 2  # وزن أعلى
        elif macd_val < sig_val and hist_val < 0:
            bearish_count += 2
        
        # Directional Indicators
        if di_p > di_m:
            bullish_count += 1
        else:
            bearish_count += 1
        
        if bullish_count >= 3:
            return "BULLISH"
        elif bearish_count >= 3:
            return "BEARISH"
        return "NEUTRAL"
    
    def _calculate_indicator_agreement(
        self,
        trend: str,
        momentum: str,
        rsi: List[float],
        macd_line: List[float],
        signal_line: List[float],
        adx: List[float],
        stoch_k: List[float],
        stoch_d: List[float]
    ) -> float:
        """حساب نسبة اتفاق المؤشرات (0-100)"""
        agreements = []
        
        # 1. RSI
        rsi_val = rsi[-1] if rsi else 50
        if trend == "BULLISH" and 30 < rsi_val < 70:
            agreements.append(True)
        elif trend == "BEARISH" and 30 < rsi_val < 70:
            agreements.append(True)
        elif trend == "NEUTRAL":
            agreements.append(True)
        else:
            agreements.append(False)
        
        # 2. MACD
        if macd_line and signal_line:
            macd_val = macd_line[-1]
            sig_val = signal_line[-1]
            if (trend == "BULLISH" and macd_val > sig_val) or \
               (trend == "BEARISH" and macd_val < sig_val):
                agreements.append(True)
            else:
                agreements.append(False)
        
        # 3. Stochastic
        if stoch_k and stoch_d:
            k = stoch_k[-1]
            d = stoch_d[-1]
            if (trend == "BULLISH" and k > d) or \
               (trend == "BEARISH" and k < d):
                agreements.append(True)
            else:
                agreements.append(False)
        
        # 4. ADX
        adx_val = adx[-1] if adx else 0
        if adx_val > 20:
            agreements.append(True)
        else:
            agreements.append(False)
        
        agreement_count = sum(agreements)
        total = len(agreements) if agreements else 1
        
        return (agreement_count / total) * 100
    
    def _determine_signal(
        self,
        trend: str,
        momentum: str,
        market_condition: MarketCondition,
        current_price: float,
        sr_analysis: Dict[str, Any],
        atr: List[float],
        rsi: List[float]
    ) -> Tuple[str, float, float, float, float]:
        """تحديد تفاصيل Signal"""
        # لا إشارة في السوق الضعيف
        if market_condition in [MarketCondition.RANGING, MarketCondition.UNKNOWN]:
            if trend == "NEUTRAL" and momentum == "NEUTRAL":
                return "NO_TRADE", current_price, 0, 0, 0
        
        atr_val = atr[-1] if atr else current_price * 0.005
        rsi_val = rsi[-1] if rsi else 50
        
        # شروط الشراء المحسنة
        if trend == "BULLISH" and momentum == "BULLISH":
            entry = current_price
            
            # وقف الخسارة الذكي
            sl_candidates = []
            
            # 1. تحت الدعم القريب
            if sr_analysis["nearest_support"] > 0:
                sl_candidates.append(sr_analysis["nearest_support"])
            
            # 2. باستخدام ATR
            sl_candidates.append(current_price - atr_val * self.gold_analyzer.get_atr_multiplier("normal"))
            
            # اختيار أفضل وقف
            sl = max(sl_candidates) if sl_candidates else current_price - atr_val * 2
            
            # ضمان حد أدنى للمسافة
            min_sl_distance = atr_val * 1.5
            if current_price - sl < min_sl_distance:
                sl = current_price - min_sl_distance
            
            # مستويات جني الأرباح
            sl_distance = entry - sl
            tp1 = entry + sl_distance * 1.5
            tp2 = entry + sl_distance * 2.5
            
            # تعديل TP2 إذا كان قريباً جداً من المقاومة
            if sr_analysis["nearest_resistance"] > 0:
                resistance_distance = sr_analysis["nearest_resistance"] - entry
                if resistance_distance < sl_distance * 2:
                    tp2 = min(tp2, sr_analysis["nearest_resistance"] * 0.98)
            
            return "BUY", entry, sl, tp1, tp2
        
        # شروط البيع المحسنة
        elif trend == "BEARISH" and momentum == "BEARISH":
            entry = current_price
            
            # وقف الخسارة الذكي
            sl_candidates = []
            
            # 1. فوق المقاومة القريبة
            if sr_analysis["nearest_resistance"] > 0:
                sl_candidates.append(sr_analysis["nearest_resistance"])
            
            # 2. باستخدام ATR
            sl_candidates.append(current_price + atr_val * self.gold_analyzer.get_atr_multiplier("normal"))
            
            # اختيار أفضل وقف
            sl = min(sl_candidates) if sl_candidates else current_price + atr_val * 2
            
            # ضمان حد أدنى للمسافة
            min_sl_distance = atr_val * 1.5
            if sl - current_price < min_sl_distance:
                sl = current_price + min_sl_distance
            
            # مستويات جني الأرباح
            sl_distance = sl - entry
            tp1 = entry - sl_distance * 1.5
            tp2 = entry - sl_distance * 2.5
            
            # تعديل TP2 إذا كان قريباً جداً من الدعم
            if sr_analysis["nearest_support"] > 0:
                support_distance = entry - sr_analysis["nearest_support"]
                if support_distance < sl_distance * 2:
                    tp2 = max(tp2, sr_analysis["nearest_support"] * 1.02)
            
            return "SELL", entry, sl, tp1, tp2
        
        return "NO_TRADE", current_price, 0, 0, 0
    
    def _calculate_lot_size(
        self,
        balance: float,
        risk_percent: float,
        entry_price: float,
        stop_loss: float,
        symbol: str
    ) -> float:
        """حساب حجم اللوت مع مراعاة نوع الأداة"""
        if entry_price == 0 or stop_loss == 0 or entry_price == stop_loss:
            return 0.01
        
        # حساب النقاط
        pip_size = self.gold_analyzer.GOLD_PIP_VALUE if symbol == "XAUUSD" else 0.0001
        sl_distance = abs(entry_price - stop_loss)
        sl_pips = sl_distance / pip_size
        
        if sl_pips <= 0:
            return 0.01
        
        # حساب مبلغ المخاطر
        risk_amount = balance * (risk_percent / 100)
        
        # حساب قيمة النقطة بالدولار
        if symbol == "XAUUSD":
            pip_value_usd = pip_size * self.gold_analyzer.GOLD_LOT_SIZE  # 0.01 * 100 = 1
        else:
            pip_value_usd = pip_size * 100000  # Forex standard lot
        
        # حساب اللوت
        lot_size = risk_amount / (sl_pips * pip_value_usd)
        
        # تحديد الحدود
        return max(0.01, min(lot_size, 10.0))
    
    def _calculate_risk_reward(
        self,
        entry: float,
        stop_loss: float,
        take_profit: float
    ) -> float:
        """حساب نسبة المخاطرة/المكافأة"""
        if stop_loss == 0 or entry == stop_loss:
            return 0
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    def _generate_comprehensive_explanation(
        self,
        signal_type: str,
        trend: str,
        momentum: str,
        market_condition: MarketCondition,
        rsi: float,
        adx: float,
        sr_analysis: Dict[str, Any],
        confidence: float,
        quality: SignalQuality,
        atr: float,
        risk_reward: float
    ) -> str:
        """توليد تفسير كامل ومفصل بالعربية"""
        
        if signal_type == "NO_TRADE":
            return "لا توجد فرصة تداول مناسبة حالياً. انتظر حتى تتحسنConditions."
        
        lines = []
        
        # العنوان
        signal_text = "شراء" if signal_type == "BUY" else "بيع"
        lines.append(f"📊 تحليل إشارة {signal_text}")
        lines.append("=" * 40)
        
        # 1. ملخص الإشارة
        lines.append(f"\n🎯 نوع الإشارة: {signal_text}")
        lines.append(f"📈 جودة الإشارة: {quality.value}")
        lines.append(f"⭐ مستوى الثقة: {confidence:.0f}%")
        lines.append(f"📉 نسبة المخاطرة/المكافأة: 1:{risk_reward:.2f}")
        
        # 2. ظروف السوق
        condition_names = {
            MarketCondition.TRENDING_UP: "اتجاه صاعد قوي",
            MarketCondition.TRENDING_DOWN: "اتجاه هابط قوي",
            MarketCondition.RANGING: "سوق جانبي",
            MarketCondition.VOLATILE: "سوق متقلب",
            MarketCondition.UNKNOWN: "غير محدد"
        }
        lines.append(f"\n🌡️ ظروف السوق: {condition_names.get(market_condition, 'غير محدد')}")
        
        # 3. تحليل الاتجاه
        trend_desc = {
            "BULLISH": "صاعد",
            "BEARISH": "هابط",
            "NEUTRAL": "جانبي"
        }
        lines.append(f"📊 الاتجاه العام: {trend_desc.get(trend, 'غير محدد')}")
        
        # 4. تحليل الزخم
        momentum_desc = {
            "BULLISH": "إيجابي قوي",
            "BEARISH": "سلبي قوي",
            "NEUTRAL": "محايد"
        }
        lines.append(f"💪 الزخم: {momentum_desc.get(momentum, 'غير محدد')}")
        
        # 5. المؤشرات الفنية
        lines.append(f"\n📉 المؤشرات الفنية:")
        lines.append(f"   • RSI: {rsi:.1f} ({self._get_rsi_zone(rsi)})")
        lines.append(f"   • ADX: {adx:.1f} ({self._get_adx_strength(adx)})")
        lines.append(f"   • ATR: {atr:.2f}")
        
        # 6. مستويات الدعم والمقاومة
        if sr_analysis["nearest_support"] > 0:
            lines.append(f"\n🔵 أقرب مستوى دعم: {sr_analysis['nearest_support']:.2f}")
        if sr_analysis["nearest_resistance"] > 0:
            lines.append(f"🔴 أقرب مستوى مقاومة: {sr_analysis['nearest_resistance']:.2f}")
        
        # 7. التوصية
        lines.append(f"\n💡 التوصية:")
        if signal_type == "BUY":
            lines.append("   ✅ فرصة شراء محتملة")
            if rsi < 40:
                lines.append("   ⚡ RSI يشير لمنطقة تشبع بيع - تأكيد قوة الشراء")
        else:
            lines.append("   ✅ فرصة بيع محتملة")
            if rsi > 60:
                lines.append("   ⚡ RSI يشير لمنطقة تشبع شراء - تأكيد قوة البيع")
        
        # 8. ملاحظة مهمة
        if confidence >= 75:
            lines.append(f"\n✨ إشارة عالية الجودة - مناسبة للمتاجرة")
        elif confidence >= 60:
            lines.append(f"\n⚠️ إشارة متوسطة الجودة - إدارة مخاطر حريصة")
        else:
            lines.append(f"\n⚠️ إشارة منخفضة الجودة - انتظر فرص أفضل")
        
        return "\n".join(lines)
    
    def _get_rsi_zone(self, rsi: float) -> str:
        """تحديد منطقة RSI"""
        if rsi < 30:
            return "تشبع بيع قوي"
        elif rsi < 40:
            return "تشبع بيع"
        elif rsi > 70:
            return "تشبع شراء قوي"
        elif rsi > 60:
            return "تشبع شراء"
        return "منطقة محايدة"
    
    def _get_adx_strength(self, adx: float) -> str:
        """تحديد قوة ADX"""
        if adx >= 40:
            return "اتجاه قوي جداً"
        elif adx >= 25:
            return "اتجاه قوي"
        elif adx >= 20:
            return "اتجاه متوسط"
        return "اتجاه ضعيف"
    
    def _generate_rejection_reason(
        self,
        trend: str,
        momentum: str,
        market_condition: MarketCondition,
        confidence: float,
        warnings: List[str]
    ) -> str:
        """توليد سبب رفض الإشارة"""
        reasons = []
        
        if market_condition == MarketCondition.RANGING:
            reasons.append("السوق في وضع جانبي (Ranging) - لا يوجد اتجاه واضح")
        elif market_condition == MarketCondition.VOLATILE:
            reasons.append("السوق متقلب جداً - انتظر استقرارConditions")
        
        if trend == "NEUTRAL" and momentum == "NEUTRAL":
            reasons.append("الاتجاه والزخم محايدان - لا يوجد تأكيد كافٍ")
        
        if confidence < 60:
            reasons.append(f"مستوى الثقة ({confidence:.0f}%) أقل من الحد الأدنى (60%)")
        
        for warning in warnings:
            if warning not in reasons:
                reasons.append(warning)
        
        if not reasons:
            reasons.append("الظروفConditions غير مناسبة لتوليد إشارة trading")
        
        return "\n".join([f"❌ {r}" for r in reasons])
    
    def _no_trade_result(self, explanation: str, market_condition: str) -> SignalResult:
        """إرجاع نتيجة لا يوجد تداول"""
        return SignalResult(
            signal_type="NO_TRADE",
            entry_price=0,
            stop_loss=0,
            take_profit_1=0,
            take_profit_2=0,
            lot_size=0,
            confidence=0,
            explanation=explanation,
            indicators={},
            trend="NEUTRAL",
            market_condition=market_condition,
            signal_quality="REJECTED",
            risk_reward_ratio=0,
            warning_messages=["لا توجد فرصة تداول حالياً"],
            timestamp=datetime.now().isoformat()
        )


# إنشاء مثيل عام للمحرك المحسن
enhanced_signal_generator = EnhancedSignalGenerator()