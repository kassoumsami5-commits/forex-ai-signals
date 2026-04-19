"""
خدمة بيانات السوق - طبقة التجريد لبيانات السوق
تدعم مزودين: TwelveData (الفعلي) و Mock (البديل)
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import httpx
from ..config import settings


class MarketDataProvider(ABC):
    """الفئة الأساسية لموفر بيانات السوق"""
    
    @abstractmethod
    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """الحصول على السعر الحالي"""
        pass
    
    @abstractmethod
    async def get_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        output_size: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """الحصول على البيانات التاريخية"""
        pass


class TwelveDataProvider(MarketDataProvider):
    """مزود TwelveData لبيانات السوق الحقيقية"""
    
    def __init__(self):
        self.api_key = settings.TWELVEDATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
    
    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على السعر الحالي من TwelveData
        
        Args:
            symbol: رمز السوق (مثال: XAUUSD, EURUSD)
        
        Returns:
            قاموس يحتوي على السعر والبيانات المطلوبة أو None في حالة الفشل
        """
        if not self.api_key or self.api_key == "your_twelvedata_api_key":
            return None
        
        url = f"{self.base_url}/price"
        params = {
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "symbol": symbol,
                        "price": float(data.get("price", 0)),
                        "timestamp": data.get("timestamp")
                    }
                return None
        except Exception as e:
            print(f"خطأ في جلب السعر من TwelveData: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        output_size: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        الحصول على البيانات التاريخية من TwelveData
        
        Args:
            symbol: رمز السوق
            interval: الفترة الزمنية (1min, 5min, 1h, 1day, etc.)
            output_size: عدد الشموع المطلوب
        
        Returns:
            قائمة من القواميس تحتوي على بيانات الشموع أو None في حالة الفشل
        """
        if not self.api_key or self.api_key == "your_twelvedata_api_key":
            return None
        
        url = f"{self.base_url}/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": output_size,
            "format": "json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if "values" in data:
                        candles = []
                        for item in data["values"]:
                            candles.append({
                                "datetime": item.get("datetime"),
                                "open": float(item.get("open", 0)),
                                "high": float(item.get("high", 0)),
                                "low": float(item.get("low", 0)),
                                "close": float(item.get("close", 0)),
                                "volume": float(item.get("volume", 0)) if item.get("volume") else 0
                            })
                        return candles
                return None
        except Exception as e:
            print(f"خطأ في جلب البيانات التاريخية من TwelveData: {e}")
            return None


class MockMarketDataProvider(MarketDataProvider):
    """مزود البيانات الوهمية للاختبار والتطوير"""
    
    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        إنشاء سعر وهمي للسوق
        
        الأسعار الوهمية:
        - XAUUSD (الذهب): حوالي 2300
        - EURUSD: حوالي 1.08
        - BTCUSD: حوالي 65000
        """
        mock_prices = {
            "XAUUSD": {"base": 2300.0, "spread": 0.5},
            "EURUSD": {"base": 1.0850, "spread": 0.0002},
            "GBPUSD": {"base": 1.2650, "spread": 0.0003},
            "USDJPY": {"base": 154.50, "spread": 0.02},
            "BTCUSD": {"base": 65000.0, "spread": 50.0},
        }
        
        import random
        from datetime import datetime
        
        if symbol in mock_prices:
            price_data = mock_prices[symbol]
            variation = random.uniform(-0.01, 0.01) * price_data["base"]
            price = price_data["base"] + variation
            
            return {
                "symbol": symbol,
                "price": round(price, 4),
                "bid": round(price - price_data["spread"]/2, 4),
                "ask": round(price + price_data["spread"]/2, 4),
                "timestamp": datetime.now().isoformat(),
                "change_percent": round(random.uniform(-2, 2), 2)
            }
        
        return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        output_size: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        إنشاء بيانات تاريخية وهمية realistic
        """
        import random
        from datetime import datetime, timedelta
        
        mock_prices = {
            "XAUUSD": 2300.0,
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 154.50,
            "BTCUSD": 65000.0,
        }
        
        base_price = mock_prices.get(symbol, 100.0)
        
        candles = []
        current_price = base_price
        now = datetime.now()
        
        # تحديد حجم الخطوة بناءً على الفترة الزمنية
        interval_seconds = {
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "30min": 1800,
            "1h": 3600,
            "4h": 14400,
            "1day": 86400,
        }
        
        step = interval_seconds.get(interval, 3600)
        
        for i in range(output_size):
            timestamp = now - timedelta(seconds=step * (output_size - i))
            
            # محاكاة حركة السعر
            change = random.gauss(0, base_price * 0.002)
            open_price = current_price
            close_price = current_price + change
            
            # إنشاء High و Low
            high_price = max(open_price, close_price) + abs(random.gauss(0, base_price * 0.001))
            low_price = min(open_price, close_price) - abs(random.gauss(0, base_price * 0.001))
            
            candles.append({
                "datetime": timestamp.isoformat(),
                "open": round(open_price, 4),
                "high": round(high_price, 4),
                "low": round(low_price, 4),
                "close": round(close_price, 4),
                "volume": round(random.uniform(100, 10000), 2)
            })
            
            current_price = close_price
        
        return candles


def get_market_data_provider() -> MarketDataProvider:
    """
    الحصول على مزود بيانات السوق المناسب
    
    يستخدم TwelveData إذا كان المفتاح متوفراً، وإلا يستخدم المزود الوهمي
    """
    if settings.TWELVEDATA_API_KEY and settings.TWELVEDATA_API_KEY != "your_twelvedata_api_key":
        return TwelveDataProvider()
    return MockMarketDataProvider()


class MarketDataService:
    """خدمة بيانات السوق للتفاعل مع الواجهة"""
    
    def __init__(self):
        self.provider = get_market_data_provider()
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        الحصول على السعر الحالي مع معالجة الأخطاء
        """
        result = await self.provider.get_realtime_price(symbol)
        
        if result is None:
            # في حالة الفشل، نعيد سعر افتراضي
            return {
                "symbol": symbol,
                "price": 0,
                "error": "تعذر الحصول على بيانات السوق"
            }
        
        return result
    
    async def get_candles(
        self, 
        symbol: str, 
        timeframe: str, 
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        الحصول على بيانات الشموع مع معالجة الأخطاء
        """
        result = await self.provider.get_historical_data(
            symbol, 
            timeframe, 
            count
        )
        
        if result is None:
            return []
        
        return result
    
    async def get_market_overview(self) -> List[Dict[str, Any]]:
        """
        الحصول على نظرة عامة على السوق
        """
        symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD"]
        overview = []
        
        for symbol in symbols:
            data = await self.get_current_price(symbol)
            overview.append(data)
        
        return overview


# إنشاء مثيل عام لخدمة بيانات السوق
market_data_service = MarketDataService()