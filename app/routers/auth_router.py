from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import User
from app.schemas.user import UserResponse, Token, VKAuthRequest
from app.schemas.deal import DealResponse
from app.services.vk_auth_service import get_vk_user_info, authenticate_vk_user
from app.services.auth_service import create_access_token, get_current_user
from app.services.deal_service import get_user_deals, get_shared_deals_for_user
from app.core.config import VK_CLIENT_ID, VK_REDIRECT_URI

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.get("/vk/login")
async def vk_login():
    """
    Получить URL для авторизации через VK
    """
    vk_auth_url = (
        f"https://oauth.vk.com/authorize"
        f"?client_id={VK_CLIENT_ID}"
        f"&redirect_uri={VK_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=email"
        f"&v=5.131"
    )
    return {"authorization_url": vk_auth_url}


@router.post("/vk/callback", response_model=Token)
async def vk_callback(request: VKAuthRequest, db: Session = Depends(get_db)):
    """
    Обработка callback от VK после авторизации
    """
    # Получаем информацию о пользователе из VK
    vk_user_info = await get_vk_user_info(request.code)
    
    if not vk_user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with VK"
        )
    
    # Аутентифицируем пользователя и получаем токен
    user, access_token = authenticate_vk_user(db, vk_user_info)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе
    """
    return current_user


@router.get("/me/deals", response_model=List[DealResponse])
async def get_my_deals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить все сделки текущего пользователя
    """
    owned_deals = get_user_deals(db, current_user.id)
    shared_deals = get_shared_deals_for_user(db, current_user.id)
    
    # Объединяем и убираем дубликаты
    all_deals = {deal.id: deal for deal in owned_deals + shared_deals}
    return list(all_deals.values())


@router.post("/logout")
async def logout():
    """
    Выход из системы (клиент должен удалить токен)
    """
    return {"message": "Successfully logged out"}
