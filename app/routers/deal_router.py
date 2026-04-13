from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import User, Deal
from app.schemas.deal import (
    DealCreate,
    DealUpdate,
    DealResponse,
    ShareDealRequest,
    SharedDealResponse,
)
from app.services.auth_service import get_current_user
from app.services.deal_service import (
    create_deal,
    get_deal_by_id,
    get_user_deals,
    update_deal,
    delete_deal,
    generate_share_token,
    get_deal_by_share_token,
    share_deal_with_user,
    upload_deal_info,
)

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("/", response_model=DealResponse)
async def create_new_deal(
    deal_data: DealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новую сделку
    """
    deal = create_deal(db, deal_data.model_dump(), current_user.id)
    return deal


@router.get("/", response_model=List[DealResponse])
async def get_all_user_deals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить все сделки текущего пользователя
    """
    deals = get_user_deals(db, current_user.id)
    return deals


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить сделку по ID
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this deal"
        )
    
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
async def update_existing_deal(
    deal_id: int,
    deal_update: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о сделке
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to update this deal"
        )
    
    updated_deal = update_deal(db, deal_id, deal_update.model_dump(exclude_unset=True))
    return updated_deal


@router.delete("/{deal_id}")
async def delete_existing_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить сделку
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to delete this deal"
        )
    
    delete_deal(db, deal_id)
    return {"message": "Deal deleted successfully"}


@router.post("/{deal_id}/share", response_model=dict)
async def share_deal_link(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Поделиться ссылкой на сделку (генерация токена для доступа)
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to share this deal"
        )
    
    share_token = generate_share_token(db, deal_id)
    
    share_url = f"/deals/shared/{share_token}"
    
    return {
        "message": "Share link generated successfully",
        "share_url": share_url,
        "share_token": share_token
    }


@router.post("/{deal_id}/share-with-user", response_model=SharedDealResponse)
async def share_deal_with_specific_user(
    deal_id: int,
    share_request: ShareDealRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Поделиться сделкой с конкретным пользователем
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to share this deal"
        )
    
    shared_deal = share_deal_with_user(
        db, 
        deal_id, 
        share_request.user_id, 
        share_request.access_level
    )
    
    return shared_deal


@router.post("/{deal_id}/upload-info", response_model=DealResponse)
async def upload_deal_information(
    deal_id: int,
    info_data: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузить/обновить информацию о сделке
    """
    deal = get_deal_by_id(db, deal_id)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Проверяем права доступа
    if deal.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to update this deal"
        )
    
    updated_deal = upload_deal_info(db, deal_id, info_data.model_dump(exclude_unset=True))
    return updated_deal


# Публичный доступ к сделке по токену
@router.get("/shared/{share_token}", response_model=DealResponse)
async def get_shared_deal(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    Получить сделку по ссылке с токеном (публичный доступ)
    """
    deal = get_deal_by_share_token(db, share_token)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found or invalid share token"
        )
    
    return deal
