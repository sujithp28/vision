"""Video result model for VisionForge"""

from sqlalchemy import Column, String, JSON, Boolean, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, BaseModel


class VideoResult(BaseModel):
    """Generated video result with metadata"""
    
    __tablename__ = "video_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    prompt = Column(String(2000), nullable=False)
    video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(String(1000), nullable=True)
    provider = Column(String(50), nullable=True)  # Which AI provider generated
    duration_seconds = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional metadata (quality, format, etc)
    
    # Indices for common queries
    __table_args__ = (
        Index('idx_video_user_id', 'user_id'),
        Index('idx_video_status', 'status'),
    )
    
    def __repr__(self):
        return f"<VideoResult {self.id[:8]}...>"
