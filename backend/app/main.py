"""
تطبيق FastAPI الرئيسي -Forex AI Signals
نقطة الدخول للتطبيق مع جميع المسارات والإعدادات
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from .database import async_engine, Base
from .config import settings
from .routes import auth, analysis, subscription, webhook

# إعداد logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق
    يتم تنفيذ هذا عند بدء وإيقاف التطبيق
    """
    # عند البدء
    logger.info("جاري بدء التطبيق...")
    
    try:
        # إنشاء الجداول في قاعدة البيانات
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"خطأ في إنشاء جداول قاعدة البيانات: {e}")
    
    yield
    
    # عند الإيقاف
    logger.info("جاري إيقاف التطبيق...")
    await async_engine.dispose()
    logger.info("تم تنظيف الموارد بنجاح")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Forex AI Signals API",
    description="""
## منصة إشارات التداول بالذكاء الاصطناعي
    
### الميزات الرئيسية:
- 🔐 **مصادقة JWT** - تسجيل دخول وتسجيل آمن
- 📊 **تحليل السوق** - بيانات حية من مزودين متعددين
- 📈 **توليد الإشارات** - تحليل فني متقدم باستخدام مؤشرات متعددة
- 🔢 **حاسبة اللوت** - حساب حجم الصفقة الأمثل
- 💰 **إدارة الاشتراكات** - خطط Free و Pro و VIP
- 🔔 **تكامل TradingView** - استقبال إشعارات TradingView عبر Webhook
- 📜 **سجل الإشارات** - تخزين وتصفية الإشارات السابقة

### الأمان:
- تشفير كلمات المرور باستخدام bcrypt
- رموز JWT للتفاعل مع API
- حماية مسارات حسب مستوى الاشتراك

### للتطوير:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# إضافة Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_handler(request: Request, exc: Exception):
    """معالجة خطأ عدم الصلاحية"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "غير مصرح بالوصول",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(status.HTTP_403_FORBIDDEN)
async def forbidden_handler(request: Request, exc: Exception):
    """معالجة خطأ الحظر"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": "غير مسموح بهذا الإجراء",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: Exception):
    """معالجة خطأ عدم العثور"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "المورد غير موجود",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """معالجة الأخطاء العامة"""
    logger.error(f"خطأ غير متوقع: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "حدث خطأ داخلي غير متوقع",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


# Root endpoint
@app.get("/", tags=["الرئيسية"])
async def root():
    """
    الصفحة الرئيسية لـ API
    """
    return {
        "name": "Forex AI Signals API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", tags=["الرئيسية"])
async def health_check():
    """
    فحص صحة التطبيق
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if settings.DATABASE_URL else "disconnected",
        "version": "1.0.0"
    }


# مسارات API
app.include_router(auth.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(analysis.market_router, prefix="/api")
app.include_router(analysis.calculator_router, prefix="/api")
app.include_router(subscription.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")


# Endpoint لمعلومات المستخدم (للاختبار)
@app.get("/api/test-auth", tags=["الاختبار"])
async def test_auth():
    """
    اختبار الاتصال
    """
    return {
        "message": "API يعمل بنجاح",
        "timestamp": datetime.now().isoformat()
    }


# Endpoint لتوليد مستخدم تجريبي
@app.post("/api/create-demo-user", tags=["الاختبار"])
async def create_demo_user():
    """
    إنشاء مستخدم تجريبي للاختبار
    """
    from .database import get_db
    from .models import User
    from .core.security import hash_password
    from sqlalchemy import select
    
    async for db in get_db():
        # التحقق من وجود المستخدم
        result = await db.execute(
            select(User).where(User.email == "demo@forexai.local")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return {
                "message": "المستخدم التجريبي موجود بالفعل",
                "email": "demo@forexai.local",
                "password": "demo123"
            }
        
        # إنشاء المستخدم
        demo_user = User(
            email="demo@forexai.local",
            hashed_password=hash_password("demo123"),
            full_name="مستخدم تجريبي",
            subscription_tier="pro"
        )
        
        db.add(demo_user)
        await db.commit()
        await db.refresh(demo_user)
        
        return {
            "message": "تم إنشاء المستخدم التجريبي بنجاح",
            "email": "demo@forexai.local",
            "password": "demo123",
            "tier": "pro"
        }