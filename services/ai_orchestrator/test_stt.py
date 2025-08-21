"""
Test suite for STT service
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from stt_service import STTService, STTConfig, ProfanityFilter

class TestSTTService:
    
    @pytest.fixture
    def stt_service(self):
        """Create STT service instance for testing"""
        return STTService()
    
    @pytest.fixture
    def sample_audio(self):
        """Create sample audio data for testing"""
        # Create a simple WAV file header with silence
        wav_header = b'RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00'
        return wav_header
    
    def test_profanity_filter(self):
        """Test profanity detection and filtering"""
        filter = ProfanityFilter()
        
        # Test clean text
        clean_text = "Hello, how are you?"
        result = filter.contains_profanity(clean_text)
        assert result["has_profanity"] == False
        assert len(result["profane_words"]) == 0
        
        # Test profanity detection
        profane_text = "This is a fucking test"
        result = filter.contains_profanity(profane_text)
        assert result["has_profanity"] == True
        assert "fucking" in result["profane_words"]
        
        # Test censored text
        assert "***" in result["clean_text"]
    
    @pytest.mark.asyncio
    async def test_transcribe_audio(self, stt_service, sample_audio):
        """Test audio transcription"""
        # Mock Google Speech API response
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_alternative = MagicMock()
        mock_alternative.transcript = "Hello world"
        mock_alternative.confidence = 0.95
        mock_result.alternatives = [mock_alternative]
        mock_response.results = [mock_result]
        
        with patch.object(stt_service.stt_client.client, 'recognize', return_value=mock_response):
            result = await stt_service.transcribe_audio_file(sample_audio, "audio/wav")
            assert result["text"] == "Hello world"
            assert result["confidence"] == 0.95
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_profanity_detection_in_transcription(self, stt_service, sample_audio):
        """Test profanity detection in transcribed text"""
        # Mock Google Speech API response with profanity
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_alternative = MagicMock()
        mock_alternative.transcript = "This is a fucking test"
        mock_alternative.confidence = 0.90
        mock_result.alternatives = [mock_alternative]
        mock_response.results = [mock_result]
        
        with patch.object(stt_service.stt_client.client, 'recognize', return_value=mock_response):
            result = await stt_service.transcribe_audio_file(sample_audio, "audio/wav")
            assert result["text"] == "This is a fucking test"
            assert result["has_profanity"] == True
            assert "fucking" in result["profane_words"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
