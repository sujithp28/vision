"""Audit log model for compliance and debugging"""

from sqlalchemy import Column, String, JSON, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, BaseModel


class AuditLog(BaseModel):
    """Audit log entry for compliance and debugging"""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # create_video, delete_video, etc
    resource_type = Column(String(50), nullable=False)  # video, image, audio, etc
    resource_id = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False)  # success, failure
    status_code = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)  # Additional metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    
    # Indices for audit queries
    __table_args__ = (
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} {self.resource_type}>"
