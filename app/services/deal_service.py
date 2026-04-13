import uuid
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import Deal, SharedDeal, User


def create_deal(db: Session, deal_data: dict, owner_id: int) -> Deal:
    """Создать новую сделку"""
    deal = Deal(
        **deal_data,
        owner_id=owner_id,
        status="draft"
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


def get_deal_by_id(db: Session, deal_id: int) -> Optional[Deal]:
    """Получить сделку по ID"""
    return db.query(Deal).filter(Deal.id == deal_id).first()


def get_user_deals(db: Session, user_id: int) -> List[Deal]:
    """Получить все сделки пользователя"""
    return db.query(Deal).filter(Deal.owner_id == user_id).all()


def update_deal(db: Session, deal_id: int, update_data: dict) -> Optional[Deal]:
    """Обновить сделку"""
    deal = get_deal_by_id(db, deal_id)
    if not deal:
        return None
    
    for key, value in update_data.items():
        setattr(deal, key, value)
    
    db.commit()
    db.refresh(deal)
    return deal


def delete_deal(db: Session, deal_id: int) -> bool:
    """Удалить сделку"""
    deal = get_deal_by_id(db, deal_id)
    if not deal:
        return False
    
    db.delete(deal)
    db.commit()
    return True


def generate_share_token(db: Session, deal_id: int) -> Optional[str]:
    """Сгенерировать токен для публикации ссылки на сделку"""
    deal = get_deal_by_id(db, deal_id)
    if not deal:
        return None
    
    share_token = str(uuid.uuid4())
    deal.share_token = share_token
    db.commit()
    db.refresh(deal)
    
    return share_token


def get_deal_by_share_token(db: Session, share_token: str) -> Optional[Deal]:
    """Получить сделку по токену доступа"""
    return db.query(Deal).filter(Deal.share_token == share_token).first()


def share_deal_with_user(
    db: Session, 
    deal_id: int, 
    user_id: int, 
    access_level: str = "view"
) -> Optional[SharedDeal]:
    """Поделиться сделкой с другим пользователем"""
    deal = get_deal_by_id(db, deal_id)
    if not deal:
        return None
    
    # Проверяем, не поделились ли уже
    existing_share = db.query(SharedDeal).filter(
        SharedDeal.deal_id == deal_id,
        SharedDeal.user_id == user_id
    ).first()
    
    if existing_share:
        existing_share.access_level = access_level
        db.commit()
        db.refresh(existing_share)
        return existing_share
    
    shared_deal = SharedDeal(
        deal_id=deal_id,
        user_id=user_id,
        access_level=access_level
    )
    db.add(shared_deal)
    db.commit()
    db.refresh(shared_deal)
    
    return shared_deal


def get_shared_deals_for_user(db: Session, user_id: int) -> List[Deal]:
    """Получить сделки, которыми поделились с пользователем"""
    shared = db.query(SharedDeal).filter(SharedDeal.user_id == user_id).all()
    deal_ids = [s.deal_id for s in shared]
    return db.query(Deal).filter(Deal.id.in_(deal_ids)).all()


def upload_deal_info(db: Session, deal_id: int, info_data: dict) -> Optional[Deal]:
    """Загрузить/обновить информацию о сделке"""
    return update_deal(db, deal_id, info_data)
