from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Optional[int] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    status: Optional[str] = None


class DealResponse(DealBase):
    id: int
    status: str
    owner_id: int
    share_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShareDealRequest(BaseModel):
    deal_id: int
    access_level: str = "view"  # view or edit


class SharedDealResponse(BaseModel):
    id: int
    deal_id: int
    user_id: int
    access_level: str
    created_at: datetime

    class Config:
        from_attributes = True
