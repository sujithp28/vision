"""API Router for LLM Endpoints.

This module defines the FastAPI routes for interacting with the LLM service.
It provides endpoints for text generation, streaming, health checks, and model information.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
import json
import logging

from ...services.llm_service import get_llm_service
from ...schemas.llm import LLMGenerateRequest, LLMGenerateResponse

router = APIRouter(prefix="/llm", tags=["llm"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=LLMGenerateResponse)
async def generate_text_endpoint(
    request: LLMGenerateRequest, llm_service=Depends(get_llm_service)
):
    """Generate text from a prompt.

    Args:
        request: The generation request containing prompt and parameters
        llm_service: The LLM service dependency

    Returns:
        LLMGenerateResponse: The generated text and metadata

    Raises:
        HTTPException: If generation fails
    """
    try:
        result = await llm_service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            **request.parameters,
        )

        return LLMGenerateResponse(
            text=result,
            model=llm_service.get_provider_info().get("model", "unknown"),
            provider=llm_service.get_provider_info().get("provider", "unknown"),
            usage=None,
        )
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}",
        )


@router.post("/generate/stream")
async def generate_text_stream_endpoint(
    request: LLMGenerateRequest, llm_service=Depends(get_llm_service)
):
    """Generate text as a stream from a prompt.

    Args:
        request: The generation request containing prompt and parameters
        llm_service: The LLM service dependency

    Returns:
        StreamingResponse: A streaming response of generated text chunks

    Raises:
        HTTPException: If streaming fails
    """

    async def generate_stream():
        try:
            async for chunk in llm_service.generate_text_stream(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                **request.parameters,
            ):
                # Format as Server-Sent Events
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            # Send final event to indicate completion
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/models")
async def get_available_models(llm_service=Depends(get_llm_service)):
    """Get list of available models from the current provider.

    Args:
        llm_service: The LLM service dependency

    Returns:
        dict: List of available models
    """
    try:
        models = await llm_service.get_available_models()
        return {
            "provider": llm_service.get_provider_info().get("provider", "unknown"),
            "models": models,
        }
    except Exception as e:
        logger.error(f"Failed to retrieve models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}",
        )


@router.get("/health")
async def llm_health_check(llm_service=Depends(get_llm_service)):
    """Check the health of the LLM service.

    Args:
        llm_service: The LLM service dependency

    Returns:
        dict: Health status information
    """
    try:
        is_healthy = await llm_service.health_check()
        if is_healthy:
            return {
                "status": "healthy",
                "provider": llm_service.get_provider_info().get("provider", "unknown"),
                "model": llm_service.get_provider_info().get("model", "unknown"),
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "service": llm_service.settings.app_name,
                    "error": "Service unhealthy",
                },
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": llm_service.settings.app_name,
                "error": str(e),
            },
        )


@router.get("/info")
async def get_llm_info(llm_service=Depends(get_llm_service)):
    """Get information about the current LLM configuration.

    Args:
        llm_service: The LLM service dependency

    Returns:
        dict: Information about the LLM setup
    """
    return llm_service.get_provider_info()


# Include the router in the main app (this would be done in main.py)
# Example usage in main.py:
# from app.api.routes.llm import router as llm_router
# app.include_router(llm_router)

# Additional routers would be included here as they are implemented
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])
#
