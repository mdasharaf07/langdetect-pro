"""
Production-ready FastAPI backend for language detection using FastText
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from dotenv import load_dotenv

from config import settings
from schemas import (
    PredictionRequest, 
    PredictionResponse, 
    HealthResponse, 
    ErrorResponse,
    LanguagePrediction,
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserInfo,
    APIKeyRegenerateRequest,
    APIKeyRegenerateResponse
)
from model import get_model, initialize_model
from utils import validate_input_text, get_sample_texts
from auth import auth_manager
from middleware import APIKeyAuthMiddleware, RequestLoggingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.get_log_file_path()),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Redis for caching (optional)
redis_client = None
if settings.REDIS_ENABLED:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    
    # Initialize model
    model_path = settings.get_model_path()
    if not initialize_model(model_path):
        logger.error(f"Failed to initialize model from {model_path}")
        logger.info("Please ensure the FastText model is available")
        raise RuntimeError("Model initialization failed")
    
    logger.info("Model loaded successfully")
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(APIKeyAuthMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


# Cache helper
def get_cache_key(text: str) -> str:
    """Generate cache key for text"""
    import hashlib
    return f"lang_detect:{hashlib.md5(text.encode()).hexdigest()}"


# API Endpoints

@app.post("/register", response_model=UserRegistrationResponse, tags=["Authentication"])
async def register_user(registration_request: UserRegistrationRequest):
    """
    Register a new user and generate API key
    
    Args:
        registration_request: User registration data
        
    Returns:
        UserRegistrationResponse with API key
    """
    try:
        # Register new user
        user = auth_manager.register_user(
            email=registration_request.email,
            name=registration_request.name,
            password=registration_request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        logger.info(f"New user registered: {user.email}")
        
        return UserRegistrationResponse(
            message="User registered successfully",
            user_id=user.id,
            api_key=user.api_key,
            rate_limit=user.rate_limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.get("/user/info", response_model=UserInfo, tags=["User"])
async def get_user_info(request: Request):
    """
    Get current user information
    
    Requires valid API key in X-API-Key header.
    """
    try:
        user = request.state.user
        
        return UserInfo(
            user_id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            last_used=user.last_used,
            request_count=user.request_count,
            rate_limit=user.rate_limit,
            is_active=user.is_active
        )
        
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@app.post("/user/regenerate-api-key", response_model=APIKeyRegenerateResponse, tags=["User"])
async def regenerate_api_key(request: Request, regen_request: APIKeyRegenerateRequest):
    """
    Regenerate API key for current user
    
    Requires valid API key in X-API-Key header.
    """
    try:
        user = request.state.user
        
        # In a real implementation, you'd verify the password
        # For now, we'll just regenerate the key
        new_api_key = auth_manager.regenerate_api_key(user.id)
        
        if not new_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to regenerate API key"
            )
        
        logger.info(f"API key regenerated for user: {user.email}")
        
        return APIKeyRegenerateResponse(
            message="API key regenerated successfully",
            new_api_key=new_api_key
        )
        
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    except Exception as e:
        logger.error(f"Failed to regenerate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate API key"
        )

@app.get("/", response_model=HealthResponse, tags=["Health"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    """
    Health check endpoint
    
    Returns API health status and model information.
    """
    try:
        model = get_model()
        
        return HealthResponse(
            status="healthy",
            model_loaded=model.is_loaded,
            timestamp=datetime.now().isoformat(),
            version=settings.APP_VERSION,
            model_path=settings.MODEL_PATH
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")
async def predict_language(request: Request, prediction_request: PredictionRequest):
    """
    Detect language of input text
    
    Args:
        prediction_request: Request containing text to analyze
        
    Returns:
        PredictionResponse with detected language and confidence scores
    """
    try:
        text = prediction_request.text
        
        # Validate input
        validation_error = validate_input_text(text)
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error
            )
        
        # Check cache first
        cache_key = None
        if redis_client:
            cache_key = get_cache_key(text)
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for key: {cache_key[:16]}...")
                    import json
                    return PredictionResponse(**json.loads(cached_result))
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        # Get model and predict
        model = get_model()
        predictions, script, status, processing_time = model.predict_with_confidence_check(text, k=3)
        
        # Convert to response format
        language_predictions = [
            LanguagePrediction(
                language=pred["language"],
                confidence=pred["confidence"]
            )
            for pred in predictions
        ]
        
        response = PredictionResponse(
            input=text,
            script=script,
            predictions=language_predictions,
            status=status,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.now().isoformat()
        )
        
        # Cache result
        if redis_client and cache_key:
            try:
                redis_client.setex(
                    cache_key, 
                    3600,  # 1 hour TTL
                    response.json()
                )
                logger.info(f"Cached result for key: {cache_key[:16]}...")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
        
        logger.info(f"Detected: {predictions[0]['language']} ({predictions[0]['confidence']:.3f})")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language prediction failed"
        )


@app.get("/languages", tags=["Information"])
@limiter.limit("30/minute")
async def get_supported_languages(request: Request):
    """
    Get list of supported languages
    
    Returns a list of languages supported by the model.
    """
    try:
        model = get_model()
        languages = model.get_supported_languages()
        
        return {
            "supported_languages": languages,
            "total_languages": len(languages),
            "model_type": "FastText",
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD
        }
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported languages"
        )


@app.get("/samples", tags=["Information"])
@limiter.limit("30/minute")
async def get_sample_texts(request: Request):
    """
    Get sample texts for testing
    
    Returns sample texts in various languages for testing purposes.
    """
    try:
        samples = get_sample_texts()
        return {
            "sample_texts": samples,
            "total_samples": len(samples),
            "purpose": "Testing and demonstration"
        }
    except Exception as e:
        logger.error(f"Failed to get sample texts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sample texts"
        )


@app.get("/stats", tags=["Information"])
@limiter.limit("30/minute")
async def get_api_stats(request: Request):
    """
    Get API statistics
    
    Returns performance and usage statistics.
    """
    try:
        stats = {
            "api_version": settings.APP_VERSION,
            "model_loaded": True,
            "cache_enabled": redis_client is not None,
            "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "supported_scripts": [
                "Latin", "Cyrillic", "Arabic", "Devanagari", 
                "Tamil", "CJK", "Hiragana", "Others"
            ],
            "performance": {
                "target_response_time_ms": "< 100",
                "model_type": "FastText",
                "cache_ttl_seconds": 3600
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
