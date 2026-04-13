from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    deals = relationship("Deal", back_populates="owner")
    shared_deals = relationship("SharedDeal", back_populates="user")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Integer, nullable=True)
    status = Column(String, default="draft")  # draft, active, completed, closed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    share_token = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="deals")


class SharedDeal(Base):
    __tablename__ = "shared_deals"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_level = Column(String, default="view")  # view, edit
    created_at = Column(DateTime, default=datetime.utcnow)

    deal = relationship("Deal", backref="shared_with")
    user = relationship("User", back_populates="shared_deals")
