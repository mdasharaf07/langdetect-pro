"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request model for language prediction"""
    text: str = Field(..., min_length=3, description="Text to analyze for language detection")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v.strip()) < 3:
            raise ValueError("Text must be at least 3 characters long")
        return v.strip()


class LanguagePrediction(BaseModel):
    """Model for individual language prediction"""
    language: str = Field(..., description="Predicted language")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class PredictionResponse(BaseModel):
    """Response model for language prediction"""
    input: str = Field(..., description="Original input text")
    script: str = Field(..., description="Detected script")
    predictions: List[LanguagePrediction] = Field(..., description="Top language predictions")
    status: str = Field(..., description="Prediction status")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Prediction timestamp")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the FastText model is loaded")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Error timestamp")


class UserRegistrationRequest(BaseModel):
    """Request model for user registration"""
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=2, description="User name")
    password: str = Field(..., min_length=6, description="User password")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class UserRegistrationResponse(BaseModel):
    """Response model for user registration"""
    message: str = Field(..., description="Registration message")
    user_id: str = Field(..., description="User ID")
    api_key: str = Field(..., description="Generated API key")
    rate_limit: int = Field(..., description="Rate limit per hour")


class UserInfo(BaseModel):
    """User information model"""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    created_at: datetime = Field(..., description="Account creation date")
    last_used: Optional[datetime] = Field(None, description="Last API usage")
    request_count: int = Field(..., description="Total requests made")
    rate_limit: int = Field(..., description="Rate limit per hour")
    is_active: bool = Field(..., description="Account status")


class APIKeyRegenerateRequest(BaseModel):
    """Request model for API key regeneration"""
    password: str = Field(..., description="User password for verification")


class APIKeyRegenerateResponse(BaseModel):
    """Response model for API key regeneration"""
    message: str = Field(..., description="Regeneration message")
    new_api_key: str = Field(..., description="Newly generated API key")
