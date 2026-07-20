"""API key model for programmatic access"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, BaseModel


class APIKey(BaseModel):
    """API key for programmatic access to VisionForge"""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key = Column(String(255), unique=True, nullable=False)  # Hashed API key
    name = Column(String(255), nullable=False)  # User-friendly name
    is_active = Column(Boolean, default=True)
    last_used_at = Column(String(50), nullable=True)  # ISO format timestamp
    
    # Indices for lookups
    __table_args__ = (
        Index('idx_api_key_user', 'user_id'),
        Index('idx_api_key_key', 'key'),
    )
    
    def __repr__(self):
        return f"<APIKey {self.name}>"
