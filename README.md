# Forex AI Signals - منصة إشارات التداول بالذكاء الاصطناعي

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-14-black.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/TypeScript-5.3+-blue.svg" alt="TypeScript">
  <img src="https://img.shields.io/badge/PostgreSQL-15+-blue.svg" alt="PostgreSQL">
</div>

## 📋 نظرة عامة

**Forex AI Signals** هي منصة متكاملة لإشارات التداول تستخدم تقنيات الذكاء الاصطناعي والتحليل الفني المتقدم لمساعدة المتداولين في اتخاذ قرارات مدروسة.

### ✨ الميزات الرئيسية

- 🎯 **توليد إشارات ذكي** - تحليل فني متقدم باستخدام EMA, RSI, MACD, ATR
- 📊 **بيانات سوق حية** - أسعار حقيقية من TwelveData API
- 💰 **حاسبة اللوت** - حساب حجم الصفقة الأمثل بناءً على إدارة المخاطر
- 🔔 **تكامل TradingView** - استقبال إشعارات TradingView عبر Webhook
- 💳 **إدارة الاشتراكات** - خطط Free, Pro, VIP
- 📱 **واجهة عربية** - تصميم RTL متجاوب مع Arabic-first UI

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Framework حديث وسريع للـ API
- **Python 3.11+** - لغة البرمجة
- **SQLAlchemy** - ORM للتعامل مع قاعدة البيانات
- **PostgreSQL** - قاعدة البيانات
- **JWT** - نظام المصادقة

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - لغة البرمجة
- **Tailwind CSS** - تنسيق UI
- **Zustand** - إدارة الحالة
- **Axios** - HTTP Client

## 🚀 البدء السريع

### المتطلبات
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (أو استخدام SQLite للاختبار)
- Docker (اختياري)

### 1. استنساخ المشروع

```bash
git clone https://github.com/your-repo/forex-ai-signals.git
cd forex-ai-signals
```

### 2. إعداد Backend

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو: venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt

# نسخ ملف البيئة
cp .env.example .env

# تعديل .env حسب إعداداتك
# DATABASE_URL=postgresql://user:pass@localhost:5432/forexai
# TWELVEDATA_API_KEY=your_api_key
```

### 3. إعداد Frontend

```bash
cd frontend

# تثبيت المكتبات
npm install

# نسخ ملف البيئة
cp .env.example .env.local
```

### 4. تشغيل التطبيق

#### الوضع المحلي (مع SQLite)

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (في Terminal جديد)
cd frontend
npm run dev
```

#### باستخدام Docker

```bash
# بناء وتشغيل الكل
docker-compose up -d

# أو بشكل منفصل
docker-compose build
docker-compose up -d
```

### 5. الوصول للتطبيق

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 هيكل المشروع

```
forex-ai-signals/
├── backend/
│   ├── app/
│   │   ├── core/          # ملفات الأمان والتكوين
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/         # نماذج قاعدة البيانات
│   │   │   └── models.py
│   │   ├── routes/        # مسارات API
│   │   │   ├── auth.py
│   │   │   ├── analysis.py
│   │   │   ├── subscription.py
│   │   │   ├── webhook.py
│   │   │   └── admin.py
│   │   ├── schemas/       # مخطوطات Pydantic
│   │   │   └── schemas.py
│   │   ├── services/      # خدمات الأعمال
│   │   │   ├── market_data.py
│   │   │   ├── signal_service.py
│   │   │   └── lot_calculator.py
│   │   ├── database.py    # إعدادات قاعدة البيانات
│   │   └── main.py        # نقطة الدخول
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── login/
│   │   ├── register/
│   │   ├── signals/
│   │   ├── calculator/
│   │   ├── pricing/
│   │   └── page.tsx
│   ├── components/
│   ├── contexts/
│   ├── services/
│   ├── .env.example
│   ├── package.json
│   └── ...
├── docker-compose.yml
├── README.md
└── LICENSE
```

## 🔐 بيانات الاختبار

### مستخدم تجريبي
```
Email: demo@forexai.local
Password: demo123
Tier: Pro
```

### مستخدم Admin
```
Email: admin@forexai.local
Password: admin123
Role: Admin
```

## 📡 API Endpoints

### المصادقة
- `POST /api/auth/register` - تسجيل مستخدم جديد
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/auth/logout` - تسجيل الخروج
- `GET /api/auth/me` - معلومات المستخدم الحالي

### الإشارات
- `POST /api/signals/generate` - توليد إشارة جديدة
- `GET /api/signals/history` - سجل الإشارات
- `GET /api/signals/latest` - آخر الإشارات
- `PATCH /api/signals/{id}/status` - تحديث حالة الإشارة
- `GET /api/signals/stats` - إحصائيات الإشارات

### السوق
- `GET /api/market/overview` - نظرة عامة على السوق
- `GET /api/market/price/{symbol}` - سعر زوج عملات محدد
- `GET /api/market/candles/{symbol}` - بيانات الشموع

### حاسبة اللوت
- `POST /api/calculator/lot-size` - حساب حجم اللوت

### الاشتراكات
- `GET /api/subscriptions/plans` - جميع خطط الاشتراك
- `POST /api/subscriptions/subscribe` - الاشتراك في خطة
- `GET /api/subscriptions/my` - اشتراكي الحالي

### Webhook (TradingView)
- `POST /api/webhook/tradingview` - استقبال إشعار TradingView
- `GET /api/webhook/logs` - سجل Webhooks

### Admin
- `GET /api/admin/dashboard` - لوحة تحكم المشرف
- `GET /api/admin/users` - قائمة المستخدمين
- `GET /api/admin/signals` - جميع الإشارات

## 🎯 مثال على Webhook Payload من TradingView

```json
{
  "symbol": "XAUUSD",
  "timeframe": "1h",
  "trigger": "Buy",
  "price": 2350.50,
  "volume": 1500,
  "bar_time": "2024-01-15T10:00:00",
  "text": "Buy signal on XAUUSD - Golden cross detected"
}
```

## 🔧 متغيرات البيئة

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/forexai
USE_SQLITE=true  # للاختبار المحلي بدون PostgreSQL

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Market Data Provider
TWELVEDATA_API_KEY=your_twelvedata_api_key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 📊 قاعدة البيانات

### Schema Overview

```
users
├── id (PK)
├── email (unique)
├── hashed_password
├── full_name
├── subscription_tier (free/pro/vip)
├── is_admin
├── is_active
├── created_at
└── last_login

signals
├── id (PK)
├── user_id (FK)
├── symbol
├── signal_type (BUY/SELL/NO_TRADE)
├── entry_price
├── stop_loss
├── take_profit_1
├── take_profit_2
├── lot_size
├── confidence (0-100)
├── timeframe
├── status (pending/active/completed/cancelled)
├── trend (BULLISH/BEARISH/NEUTRAL)
├── explanation
├── indicators_data (JSON)
├── source (manual/tradingview)
├── created_at
└── updated_at

subscriptions
├── id (PK)
├── user_id (FK)
├── tier
├── status
├── start_date
├── end_date
├── auto_renew
└── payment_method

webhook_logs
├── id (PK)
├── provider
├── event_type
├── payload (JSON)
├── signal_id (FK, nullable)
├── status
├── validation_result (JSON)
├── error_message
├── created_at
└── ...
```

## 🧪 الاختبار

```bash
# Backend Tests
cd backend
pytest tests/ -v

# Frontend Tests
cd frontend
npm run test
```

## 📈 خط الإنتاج (Deployment)

### استخدام Docker

```bash
# إنتاج
docker-compose -f docker-compose.prod.yml up -d

# مع HTTPS (nginx + certbot)
docker-compose -f docker-compose.prod.yml -f docker-compose.https.yml up -d
```

### نشر على Cloud

#### AWS
```bash
# استخدام ECS/EC2
docker build -t forex-ai-signals .
docker push your-registry/forex-ai-signals
```

#### Railway/Render
- ربط مستودع GitHub
- إعداد متغيرات البيئة
- النشر تلقائي

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى:
1. Fork المشروع
2. إنشاء فرع للميزة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. إنشاء Pull Request

## 📄 الترخيص

هذا المشروع مرخص بموجب [MIT License](LICENSE).

## 📞 الدعم

- 📧 Email: support@forexai.local
- 💬 Discord: انضم للخادم
- 📖 Documentation: https://docs.forexai.local

---

<div align="center">
  <p>صُنع بـ ❤️ للمتداولين العرب</p>
  <p>© 2024 Forex AI Signals. جميع الحقوق محفوظة.</p>
</div>