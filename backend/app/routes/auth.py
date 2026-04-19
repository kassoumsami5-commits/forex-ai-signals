"""
مسارات المصادقة - تسجيل الدخول والتسجيل وإدارة الجلسات
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from ..core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    decode_access_token
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["المصادقة"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    الحصول على المستخدم الحالي من رمز JWT
    
    Args:
        credentials: رمز JWT في رأس الطلب
        db: جلسة قاعدة البيانات
    
    Returns:
        المستخدم الحالي
    
    Raises:
        HTTPException: في حالة عدم صلاحية الرمز
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الرمز غير صالح أو منتهي الصلاحية",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الرمز لا يحتوي على معرف المستخدم",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="معرف المستخدم غير صالح",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    تسجيل مستخدم جديد
    
    Args:
        user_data: بيانات المستخدم (البريد الإلكتروني، كلمة المرور، الاسم)
        db: جلسة قاعدة البيانات
    
    Returns:
        بيانات المستخدم المنشأ
    
    Raises:
        HTTPException: في حالة وجود مستخدم بنفس البريد الإلكتروني
    """
    # التحقق من وجود المستخدم
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مسجل مسبقاً"
        )
    
    # التحقق من تطابق كلمة المرور
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور غير متطابقة"
        )
    
    # إنشاء المستخدم
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        subscription_tier="free"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        subscription_tier=new_user.subscription_tier,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    تسجيل الدخول والحصول على رمز JWT
    
    Args:
        login_data: بيانات تسجيل الدخول (البريد الإلكتروني، كلمة المرور)
        db: جلسة قاعدة البيانات
    
    Returns:
        رمز الوصول ورمز التحديث
    
    Raises:
        HTTPException: في حالة بيانات غير صحيحة
    """
    # البحث عن المستخدم
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة"
        )
    
    # التحقق من كلمة المرور
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة"
        )
    
    # إنشاء رمز الوصول
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    تسجيل الخروج
    
    ملاحظة: في التطبيق الفعلي، قد تحتاج لتخزين الرمز في قائمة عدم الصلاحية
    """
    return {"message": "تم تسجيل الخروج بنجاح"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    الحصول على معلومات المستخدم الحالي
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    تجديد رمز الوصول
    """
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )