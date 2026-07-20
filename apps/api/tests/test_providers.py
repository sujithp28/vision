"""Tests for AI providers"""

import pytest
from packages.ai_core.providers.mock import MockProvider


@pytest.fixture
def mock_provider():
    """Create mock provider instance"""
    return MockProvider()


@pytest.mark.asyncio
async def test_mock_provider_generate(mock_provider):
    """Test mock provider text generation"""
    result = await mock_provider.generate("test prompt")
    assert result is not None
    assert len(result) > 0
    assert "Mock response" in result


@pytest.mark.asyncio
async def test_mock_provider_stream(mock_provider):
    """Test mock provider streaming"""
    chunks = []
    async for chunk in mock_provider.generate_stream("test prompt"):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


@pytest.mark.asyncio
async def test_mock_provider_health_check(mock_provider):
    """Test provider health check"""
    health = await mock_provider.health_check()
    assert health is True


def test_mock_provider_models(mock_provider):
    """Test available models list"""
    models = mock_provider.get_available_models()
    assert len(models) > 0
    assert "mock-model-1" in models
