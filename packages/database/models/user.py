"""User model for VisionForge"""

from sqlalchemy import Column, String, Boolean, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, BaseModel


class User(BaseModel):
    """User account with authentication and quotas"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    api_quota_monthly = Column(Integer, default=1000)  # Monthly API quota
    api_quota_used = Column(Integer, default=0)  # Used this month
    
    # Indices for common queries
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"
