import httpx
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.core.config import VK_CLIENT_ID, VK_CLIENT_SECRET, VK_REDIRECT_URI
from app.models.models import User
from app.services.auth_service import create_access_token


async def get_vk_user_info(code: str) -> Optional[Dict[str, Any]]:
    """Получить информацию о пользователе из VK OAuth"""
    async with httpx.AsyncClient() as client:
        try:
            # Получаем access token от VK
            token_response = await client.post(
                "https://oauth.vk.com/access_token",
                params={
                    "client_id": VK_CLIENT_ID,
                    "client_secret": VK_CLIENT_SECRET,
                    "redirect_uri": VK_REDIRECT_URI,
                    "code": code,
                }
            )
            
            if token_response.status_code != 200:
                return None
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            user_id = token_data.get("user_id")
            
            if not access_token or not user_id:
                return None
            
            # Получаем информацию о пользователе
            user_response = await client.get(
                "https://api.vk.com/method/users.get",
                params={
                    "user_ids": user_id,
                    "fields": "photo_200",
                    "access_token": access_token,
                    "v": "5.131",
                }
            )
            
            if user_response.status_code != 200:
                return None
            
            user_data = user_response.json()
            response = user_data.get("response", [])
            
            if not response:
                return None
            
            vk_user = response[0]
            return {
                "vk_id": str(user_id),
                "full_name": f"{vk_user.get('first_name', '')} {vk_user.get('last_name', '')}".strip(),
                "avatar_url": vk_user.get("photo_200"),
            }
            
        except Exception as e:
            print(f"VK OAuth error: {e}")
            return None


def authenticate_vk_user(db: Session, vk_user_info: Dict[str, Any]) -> tuple[User, str]:
    """Аутентифицировать пользователя VK и создать/обновить запись в БД"""
    vk_id = vk_user_info["vk_id"]
    
    # Проверяем, существует ли пользователь
    user = db.query(User).filter(User.vk_id == vk_id).first()
    
    if user:
        # Обновляем информацию о пользователе
        user.full_name = vk_user_info.get("full_name")
        user.avatar_url = vk_user_info.get("avatar_url")
        user.is_verified = True
        db.commit()
        db.refresh(user)
    else:
        # Создаем нового пользователя
        user = User(
            vk_id=vk_id,
            full_name=vk_user_info.get("full_name"),
            avatar_url=vk_user_info.get("avatar_url"),
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Создаем JWT токен
    access_token = create_access_token(
        data={"sub": str(user.id), "vk_id": user.vk_id}
    )
    
    return user, access_token
