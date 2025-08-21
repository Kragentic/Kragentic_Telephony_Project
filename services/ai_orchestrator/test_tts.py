"""
Tests for TTS Service
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch
from tts_service import TTSService, ResembleTTSClient, OpenAITTSClient, GTTSClient

class TestTTSService:
    
    @pytest.fixture
    def tts_service(self):
        """Create TTS service instance for testing"""
        return TTSService()
    
    @pytest.mark.asyncio
    async def test_gtts_synthesis(self, tts_service):
        """Test gTTS synthesis"""
        result = await tts_service.synthesize_speech(
            "Hello world", 
            provider="gtts"
        )
        
        assert result["audio"] is not None
        assert result["format"] == "mp3"
        assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, tts_service):
        """Test caching functionality"""
        text = "Test caching"
        
        # First call
        result1 = await tts_service.synthesize_speech(text, provider="gtts")
        assert result1["cached"] is False
        
        # Second call should be cached
        result2 = await tts_service.synthesize_speech(text, provider="gtts")
        assert result2["cached"] is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, tts_service):
        """Test health check functionality"""
        health = await tts_service.health_check()
        
        assert "status" in health
        assert "providers" in health
        assert health["providers"]["gtts"] is True
    
    @pytest.mark.asyncio
    async def test_resemble_client_missing_key(self):
        """Test Resemble client with missing API key"""
        client = ResembleTTSClient("", "", "")
        result = await client.synthesize_speech("Hello")
        
        assert result["audio"] is None
        assert "API key not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_openai_client_missing_key(self):
        """Test OpenAI client with missing API key"""
        client = OpenAITTSClient("")
        result = await client.synthesize_speech("Hello")
        
        assert result["audio"] is None
        assert "API key not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fallback_to_gtts(self, tts_service):
        """Test fallback to gTTS when provider is unavailable"""
        # Test with invalid provider
        result = await tts_service.synthesize_speech(
            "Hello world", 
            provider="invalid_provider"
        )
        
        assert result["audio"] is not None
        assert result["error"] is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
