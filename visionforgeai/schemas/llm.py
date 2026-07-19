"""Pydantic Schemas for LLM API Endpoints.

This module defines the request and response models for the LLM API endpoints,
ensuring type safety and automatic documentation generation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class LLMGenerateRequest(BaseModel):
    """Request model for text generation."""

    prompt: str = Field(
        ...,
        description="The input prompt for the language model",
        min_length=1,
        examples=["Explain the concept of machine learning in simple terms."],
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum number of tokens to generate",
        ge=1,
        le=32768,
        examples=[150],
    )
    temperature: Optional[float] = Field(
        None,
        description="Sampling temperature (0.0 to 1.0)",
        ge=0.0,
        le=2.0,
        examples=[0.7],
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific parameters",
        examples=[{"top_p": 0.9, "frequency_penalty": 0.1}],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "Write a haiku about artificial intelligence.",
                "max_tokens": 50,
                "temperature": 0.8,
                "top_p": 0.9,
            }
        }
    }


class LLMGenerateResponse(BaseModel):
    """Response model for text generation."""

    text: str = Field(
        ...,
        description="The generated text",
        examples=[
            "Silent circuits dream,\nData streams like quiet streams,\nAI dreams of electric sheep."
        ],
    )
    model: str = Field(
        ..., description="The model used for generation", examples=["gpt-4o-mini"]
    )
    provider: str = Field(
        ..., description="The provider used for generation", examples=["openai"]
    )
    usage: Optional[dict] = Field(
        None,
        description="Token usage information",
        examples=[{"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog.",
                "model": "gpt-4o-mini",
                "provider": "openai",
                "usage": {
                    "prompt_tokens": 8,
                    "completion_tokens": 9,
                    "total_tokens": 17,
                },
            }
        }
    }


class LLMStreamResponse(BaseModel):
    """Response model for streaming text generation chunks."""

    text: str = Field(..., description="A chunk of generated text", examples=["The"])
    is_complete: bool = Field(
        default=False, description="Whether this is the final chunk", examples=[False]
    )

    model_config = {
        "json_schema_extra": {"example": {"text": "Hello", "is_complete": False}}
    }


class ModelInfo(BaseModel):
    """Model information response."""

    provider: str = Field(..., description="The LLM provider", examples=["openai"])
    models: list[str] = Field(
        ...,
        description="List of available models",
        examples=[["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]],
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(
        ..., description="Health status of the service", examples=["healthy"]
    )
    provider: str = Field(..., description="The LLM provider", examples=["openai"])
    model: str = Field(
        ..., description="The current model in use", examples=["gpt-4o-mini"]
    )


class LLMInfoResponse(BaseModel):
    """LLM configuration information response."""

    provider: str = Field(..., description="The LLM provider", examples=["openai"])
    model: str = Field(
        ..., description="The configured model", examples=["gpt-4o-mini"]
    )
    temperature: float = Field(
        ..., description="The configured temperature", examples=[0.7]
    )
    max_tokens: int = Field(
        ..., description="The configured maximum tokens", examples=[2000]
    )
