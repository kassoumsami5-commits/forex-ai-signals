# Backend Deployment on Render

## Services

### Backend API
- **Repository**: https://github.com/kassoumsami5-commits/forex-ai-signals
- **Branch**: master
- **Root Directory**: backend

## Environment Variables (Required)

### Database
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.ddgejubkenewlozjqabh.supabase.co:5432/postgres
```

### JWT Security
```
JWT_SECRET_KEY=forex-ai-signals-production-secret-key-2024-secure
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### CORS
```
FRONTEND_URL=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Market Data (Optional - for real data)
```
TWELVEDATA_API_KEY=your_api_key_here
```

## Build Commands

### Backend
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Health Check

- **Path**: `/api/health` or `/docs`
- **Port**: 10000 (Render will set $PORT)

## Files Required

- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/` (all Python files)
- `backend/.env.example`

## Database Migration

The app will automatically create tables on first run via the lifespan function in `main.py`.

## Notes

- Free tier: 750 hours/month
- Instance type: Starter
- Sleep after 15 min inactivity (cold start ~30s)