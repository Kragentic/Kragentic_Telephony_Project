"""
Text-to-Speech Service using Resemble.ai and gTTS
Handles speech synthesis with caching and fallback mechanisms
"""

import os
import asyncio
import logging
from typing import Dict, Optional
import aiohttp
import base64
import hashlib
import tempfile
from datetime import datetime, timedelta
import json
from gtts import gTTS
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSConfig:
    """Configuration for TTS service"""
    def __init__(self):
        self.resemble_api_key = os.getenv('RESEMBLE_API_KEY')
        self.resemble_project_uuid = os.getenv('RESEMBLE_PROJECT_UUID')
        self.resemble_voice_uuid = os.getenv('RESEMBLE_VOICE_UUID', 'default')
        self.tts_provider = os.getenv('TTS_PROVIDER', 'resemble')  # resemble, gtts, openai
        self.cache_ttl = int(os.getenv('TTS_CACHE_TTL', '3600'))  # 1 hour default
        self.rate_limit_delay = float(os.getenv('TTS_RATE_LIMIT_DELAY', '1.0'))

class AudioCache:
    """Simple in-memory cache for audio responses"""
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[bytes]:
        """Get cached audio data"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: bytes):
        """Cache audio data"""
        self.cache[key] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def clear_expired(self):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = [k for k, v in self.cache.items() if v['expires'] < now]
        for key in expired_keys:
            del self.cache[key]

class ResembleTTSClient:
    """Resemble.ai TTS client wrapper"""
    
    def __init__(self, api_key: str, project_uuid: str, voice_uuid: str):
        self.api_key = api_key
        self.project_uuid = project_uuid
        self.voice_uuid = voice_uuid
        self.base_url = "https://app.resemble.ai/api/v1"
    
    async def synthesize_speech(self, text: str, voice_uuid: str = None) -> Dict:
        """Synthesize speech using Resemble.ai API"""
        try:
            if not self.api_key:
                return {"audio": None, "error": "Resemble.ai API key not configured"}
            
            voice_id = voice_uuid or self.voice_uuid
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': text,
                'voice_uuid': voice_id,
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
                        return {"audio": None, "error": f"Resemble.ai API error: {response.status}"}
                    
                    data = await response.json()
                    
                    # Download the audio file
                    audio_url = data.get('audio_url')
                    if audio_url:
                        async with session.get(audio_url) as audio_response:
                            if audio_response.status == 200:
                                audio_data = await audio_response.read()
                                return {
                                    "audio": base64.b64encode(audio_data).decode('utf-8'),
                                    "format": "mp3",
                                    "error": None
                                }
                    
                    return {"audio": None, "error": "Failed to download audio"}
                    
        except Exception as e:
            logger.error(f"Error synthesizing speech with Resemble.ai: {str(e)}")
            return {"audio": None, "error": str(e)}

class OpenAITTSClient:
    """OpenAI TTS client wrapper"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/audio/speech"
    
    async def synthesize_speech(self, text: str, voice: str = "alloy") -> Dict:
        """Synthesize speech using OpenAI TTS API"""
        try:
            if not self.api_key:
                return {"audio": None, "error": "OpenAI API key not configured"}
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'tts-1',
                'input': text,
                'voice': voice,
                'response_format': 'mp3',
                'speed': 1.0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        return {"audio": None, "error": f"OpenAI TTS API error: {response.status}"}
                    
                    audio_data = await response.read()
                    return {
                        "audio": base64.b64encode(audio_data).decode('utf-8'),
                        "format": "mp3",
                        "error": None
                    }
                    
        except Exception as e:
            logger.error(f"Error synthesizing speech with OpenAI: {str(e)}")
            return {"audio": None, "error": str(e)}

class GTTSClient:
    """Google TTS (gTTS) client wrapper"""
    
    async def synthesize_speech(self, text: str, lang: str = 'en') -> Dict:
        """Synthesize speech using gTTS"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to memory buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            return {
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "format": "mp3",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing speech with gTTS: {str(e)}")
            return {"audio": None, "error": str(e)}

class TTSService:
    """Main TTS service with multiple providers and caching"""
    
    def __init__(self):
        self.config = TTSConfig()
        self.cache = AudioCache(ttl=self.config.cache_ttl)
        self.resemble_client = ResembleTTSClient(
            self.config.resemble_api_key,
            self.config.resemble_project_uuid,
            self.config.resemble_voice_uuid
        )
        self.openai_client = OpenAITTSClient(os.getenv('OPENAI_API_KEY'))
        self.gtts_client = GTTSClient()
    
    def _generate_cache_key(self, text: str, provider: str, voice: str = None) -> str:
        """Generate cache key for audio data"""
        key_data = f"{text}_{provider}_{voice or 'default'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def synthesize_speech(self, text: str, provider: str = None, voice: str = None) -> Dict:
        """Synthesize speech with caching and fallback"""
        provider = provider or self.config.tts_provider
        
        # Check cache first
        cache_key = self._generate_cache_key(text, provider, voice)
        cached_audio = self.cache.get(cache_key)
        if cached_audio:
            logger.info("Returning cached audio")
            return {"audio": cached_audio, "format": "mp3", "cached": True}
        
        # Rate limiting
        await asyncio.sleep(self.config.rate_limit_delay)
        
        # Try to synthesize based on provider
        result = None
        
        if provider == 'resemble' and self.config.resemble_api_key:
            result = await self.resemble_client.synthesize_speech(text, voice)
        elif provider == 'openai' and os.getenv('OPENAI_API_KEY'):
            result = await self.openai_client.synthesize_speech(text, voice or "alloy")
        elif provider == 'gtts':
            result = await self.gtts_client.synthesize_speech(text, voice or 'en')
        else:
            # Fallback to gTTS
            logger.warning(f"Provider {provider} not available, falling back to gTTS")
            result = await self.gtts_client.synthesize_speech(text, voice or 'en')
        
        # Cache successful results
        if result.get("audio") and not result.get("error"):
            self.cache.set(cache_key, result["audio"])
        
        return result
    
    async def health_check(self) -> Dict:
        """Health check for TTS service"""
        try:
            # Test with a simple phrase
            test_result = await self.synthesize_speech("Hello world", provider="gtts")
            return {
                "status": "healthy" if test_result.get("audio") else "unhealthy",
                "providers": {
                    "resemble": bool(self.config.resemble_api_key),
                    "openai": bool(os.getenv('OPENAI_API_KEY')),
                    "gtts": True
                }
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Global service instance
tts_service = TTSService()

# Example usage
if __name__ == "__main__":
    async def test_tts():
        # Test different providers
        text = "Hello, how can I help you today?"
        
        # Test gTTS
        result = await tts_service.synthesize_speech(text, provider="gtts")
        print("gTTS result:", "success" if result.get("audio") else "failed")
        
        # Test Resemble.ai (if configured)
        if os.getenv('RESEMBLE_API_KEY'):
            result = await tts_service.synthesize_speech(text, provider="resemble")
            print("Resemble.ai result:", "success" if result.get("audio") else "failed")
    
    asyncio.run(test_tts())
