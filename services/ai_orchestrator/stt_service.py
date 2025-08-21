"""
Speech-to-Text Service using Deepgram and Resemble.ai APIs
Handles real-time transcription with profanity filtering
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
import json
import io
import tempfile
import aiohttp
import base64

from datetime import datetime
import soundfile as sf
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class STTConfig:
    """Configuration for STT service"""
    language_code: str = 'en-US'
    sample_rate_hertz: int = 16000
    encoding: str = 'LINEAR16'
    max_alternatives: int = 1
    enable_automatic_punctuation: bool = True
    profanity_filter: bool = True

class ProfanityFilter:
    """Profanity detection and filtering"""
    
    PROFANE_WORDS = {
        'fuck', 'shit', 'bitch', 'asshole', 'damn', 'hell', 
        'crap', 'piss', 'bastard', 'dick', 'pussy', 'motherfucker'
    }
    
    @staticmethod
    def contains_profanity(text: str) -> Dict[str, any]:
        """Check if text contains profanity"""
        text_lower = text.lower()
        found_words = []
        
        for word in ProfanityFilter.PROFANE_WORDS:
            if word in text_lower:
                found_words.append(word)
        
        return {
            "has_profanity": len(found_words) > 0,
            "profane_words": found_words,
            "clean_text": ProfanityFilter._censor_text(text, found_words)
        }
    
    @staticmethod
    def _censor_text(text: str, profane_words: List[str]) -> str:
        """Censor profane words in text"""
        censored = text
        for word in profane_words:
            pattern = word.lower()
            replacement = '*' * len(word)
            censored = censored.replace(word, replacement)
            censored = censored.replace(word.capitalize(), replacement)
        return censored

class DeepgramSTTClient:
    """Deepgram Speech-to-Text client wrapper"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPGRAM_API_KEY')
        self.base_url = "https://api.deepgram.com/v1/listen"
    
    async def transcribe_audio(self, audio_content: bytes) -> Dict:
        """Transcribe audio content using Deepgram API"""
        try:
            if not self.api_key:
                return {"text": "", "confidence": 0.0, "error": "Deepgram API key not configured"}
            
            headers = {
                'Authorization': f'Token {self.api_key}',
                'Content-Type': 'audio/wav'
            }
            
            params = {
                'language': 'en-US',
                'punctuate': 'true',
                'profanity_filter': 'false',
                'diarize': 'false',
                'tier': 'enhanced'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    params=params,
                    data=audio_content
                ) as response:
                    
                    if response.status != 200:
                        return {"text": "", "confidence": 0.0, "error": f"Deepgram API error: {response.status}"}
                    
                    data = await response.json()
                    
                    if not data.get('results') or not data['results'].get('channels'):
                        return {"text": "", "confidence": 0.0, "error": None}
                    
                    transcript = data['results']['channels'][0]['alternatives'][0]
                    
                    return {
                        "text": transcript.get('transcript', ''),
                        "confidence": transcript.get('confidence', 0.0),
                        "error": None
                    }
                    
        except Exception as e:
            logger.error(f"Error transcribing audio with Deepgram: {str(e)}")
            return {"text": "", "confidence": 0.0, "error": str(e)}

class ResembleTTSClient:
    """Resemble.ai Text-to-Speech client wrapper"""
    
    def __init__(self):
        self.api_key = os.getenv('RESEMBLE_API_KEY')
        self.project_uuid = os.getenv('RESEMBLE_PROJECT_UUID')
        self.base_url = "https://app.resemble.ai/api/v1"
    
    async def synthesize_speech(self, text: str, voice_uuid: str = None) -> Dict:
        """Synthesize speech using Resemble.ai API"""
        try:
            if not self.api_key:
                return {"audio": "", "error": "Resemble.ai API key not configured"}
            
            if not voice_uuid:
                voice_uuid = os.getenv('RESEMBLE_VOICE_UUID', 'default')
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': text,
                'voice_uuid': voice_uuid,
                'emotion': 'neutral',
                'precision': 'high'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/clips",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        return {"audio": "", "error": f"Resemble.ai API error: {response.status}"}
                    
                    data = await response.json()
                    
                    return {
                        "audio": data.get('audio_url', ''),
                        "clip_uuid": data.get('uuid', ''),
                        "error": None
                    }
                    
        except Exception as e:
            logger.error(f"Error synthesizing speech with Resemble.ai: {str(e)}")
            return {"audio": "", "error": str(e)}

class STTService:
    """Main STT service with Deepgram and Resemble.ai integration"""
    
    def __init__(self):
        self.config = STTConfig()
        self.deepgram_client = DeepgramSTTClient()
        self.resemble_client = ResembleTTSClient()
    
    async def transcribe_audio_file(self, audio_data: bytes, content_type: str) -> Dict:
        """Process audio file transcription using Deepgram"""
        # Convert audio to required format if needed
        audio_content = await self._convert_audio_format(audio_data, content_type)
        
        # Transcribe audio using Deepgram
        result = await self.deepgram_client.transcribe_audio(audio_content)
        
        # Check for profanity
        if result["text"]:
            profanity_check = ProfanityFilter.contains_profanity(result["text"])
            result.update(profanity_check)
        
        return result
    
    async def synthesize_speech(self, text: str, voice_uuid: str = None) -> Dict:
        """Synthesize speech using Resemble.ai"""
        return await self.resemble_client.synthesize_speech(text, voice_uuid)
    
    async def _convert_audio_format(self, audio_data: bytes, content_type: str) -> bytes:
        """Convert audio to required format (16kHz, 16-bit, mono)"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{content_type.split('/')[-1]}") as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Read and convert audio
                audio, sr = sf.read(temp_file.name)
                
                # Convert to mono if stereo
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)
                
                # Resample to 16kHz if needed
                if sr != 16000:
                    import librosa
                    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                
                # Convert to 16-bit PCM
                audio = (audio * 32767).astype(np.int16)
                
                return audio.tobytes()
                
        except Exception as e:
            logger.error(f"Error converting audio format: {str(e)}")
            return audio_data

# Global service instance
stt_service = STTService()
