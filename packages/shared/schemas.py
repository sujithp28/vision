"""Shared Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ResponseBase(BaseModel):
    """Base response model"""
    
    success: bool
    message: str
    code: str = "OK"


class ErrorResponse(ResponseBase):
    """Error response model"""
    
    success: bool = False
    error_details: Optional[dict] = None


class TimestampedModel(BaseModel):
    """Base model with timestamps"""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
