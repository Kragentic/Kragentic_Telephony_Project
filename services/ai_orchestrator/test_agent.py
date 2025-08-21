"""
Comprehensive tests for the LangChain AI Agent Service
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.ai_orchestrator.agent_service import (
    AIAgentService, 
    AgentConfig, 
    CustomerInfoInput,
    UpdateNotesInput,
    create_agent_app
)

class TestAgentConfig:
    """Test configuration for agent tests"""
    
    def __init__(self):
        self.openai_api_key = "test-openai-key"
        self.anthropic_api_key = "test-anthropic-key"
        self.primary_model = "gpt-3.5-turbo"
        self.fallback_model = "claude-3-haiku"
        self.max_tokens = 50
        self.temperature = 0.5
        self.redis_url = "redis://localhost:6379"
        self.elixir_api_url = "http://localhost:4000"

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.ping.return_value = True
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.delete.return_value = True
    return mock

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session"""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"name": "John Doe", "phone": "+1234567890"}
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session.post.return_value.__aenter__.return_value = mock_response
    return mock_session

@pytest.fixture
def agent_config():
    """Test agent configuration"""
    return TestAgentConfig()

@pytest.fixture
async def agent_service(agent_config, mock_redis):
    """Create test agent service"""
    with patch('redis.asyncio.from_url', return_value=mock_redis):
        service = AIAgentService(agent_config)
        await service.initialize()
        return service

@pytest.mark.asyncio
class TestAIAgentService:
    """Test suite for AI Agent Service"""
    
    async def test_initialization(self, agent_config, mock_redis):
        """Test service initialization"""
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            service = AIAgentService(agent_config)
            await service.initialize()
            
            assert service.redis_client is not None
            assert service.conversation_manager is not None
            assert service.customer_tools is not None
            assert service.agent_executor is not None
    
    async def test_chat_without_history(self, agent_service):
        """Test chat with no conversation history"""
        with patch.object(agent_service.llm, 'ainvoke') as mock_llm:
            mock_llm.return_value = {"output": "Hello! How can I help you?"}
            
            result = await agent_service.chat(
                message="Hi",
                conversation_id="test-conv-1"
            )
            
            assert "response" in result
            assert result["response"] == "Hello! How can I help you?"
            assert result["conversation_id"] == "test-conv-1"
            assert "timestamp" in result
    
    async def test_chat_with_phone_number(self, agent_service, mock_redis):
        """Test chat with phone number provided"""
        with patch.object(agent_service.llm, 'ainvoke') as mock_llm, \
             patch.object(agent_service.customer_tools, 'get_customer_info') as mock_get_info:
            
            mock_llm.return_value = {"output": "Hello John! How can I help you?"}
            mock_get_info.return_value = {"name": "John Doe", "phone": "+1234567890"}
            
            result = await agent_service.chat(
                message="Hi",
                conversation_id="test-conv-2",
                phone_number="+1234567890"
            )
            
            assert "response" in result
            assert result["conversation_id"] == "test-conv-2"
    
    async def test_chat_with_history(self, agent_service, mock_redis):
        """Test chat with existing conversation history"""
        # Mock Redis to return history
        history_json = json.dumps([
            {"type": "human", "content": "Hello"},
            {"type": "ai", "content": "Hi there!"}
        ])
        mock_redis.get.return_value = history_json
        
        with patch.object(agent_service.llm, 'ainvoke') as mock_llm:
            mock_llm.return_value = {"output": "How can I assist you today?"}
            
            result = await agent_service.chat(
                message="I need help",
                conversation_id="test-conv-3"
            )
            
            assert "response" in result
            assert result["conversation_id"] == "test-conv-3"
    
    async def test_chat_error_handling(self, agent_service):
        """Test error handling in chat"""
        with patch.object(agent_service.llm, 'ainvoke') as mock_llm:
            mock_llm.side_effect = Exception("API Error")
            
            result = await agent_service.chat(
                message="Hi",
                conversation_id="test-conv-4"
            )
            
            assert "response" in result
            assert "error" in result
            assert "I apologize" in result["response"]
    
    async def test_clear_conversation(self, agent_service, mock_redis):
        """Test clearing conversation history"""
        result = await agent_service.clear_conversation("test-conv-5")
        assert result is True
        mock_redis.delete.assert_called_once_with("conversation:test-conv-5")
    
    async def test_get_conversation_history(self, agent_service, mock_redis):
        """Test retrieving conversation history"""
        history_json = json.dumps([
            {"type": "human", "content": "Hello"},
            {"type": "ai", "content": "Hi there!"}
        ])
        mock_redis.get.return_value = history_json
        
        history = await agent_service.get_conversation_history("test-conv-6")
        
        assert len(history) == 2
        assert history[0]["type"] == "human"
        assert history[0]["content"] == "Hello"
        assert "timestamp" in history[0]
    
    async def test_health_check_healthy(self, agent_service, mock_redis):
        """Test health check when all services are healthy"""
        with patch.object(agent_service.llm, 'ainvoke') as mock_llm, \
             patch.object(agent_service.customer_tools, 'get_customer_info') as mock_get_info:
            
            mock_llm.return_value = "test response"
            mock_get_info.return_value = {"test": "data"}
            
            health = await agent_service.health_check()
            
            assert health["status"] == "healthy"
            assert health["redis"] == "connected"
            assert health["llm"] == "responsive"
            assert health["customer_tools"] == "accessible"
    
    async def test_health_check_unhealthy(self, agent_service, mock_redis):
        """Test health check when services are unhealthy"""
        mock_redis.ping.side_effect = Exception("Redis connection failed")
        
        health = await agent_service.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health

@pytest.mark.asyncio
class TestCustomerTools:
    """Test suite for CustomerTools"""
    
    async def test_get_customer_info_success(self):
        """Test successful customer info retrieval"""
        tools = CustomerTools("http://localhost:4000")
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"name": "John Doe", "phone": "+1234567890"}
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            result = await tools.get_customer_info("+1234567890")
            assert result["name"] == "John Doe"
    
    async def test_get_customer_info_not_found(self):
        """Test customer not found scenario"""
        tools = CustomerTools("http://localhost:4000")
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            result = await tools.get_customer_info("+1234567890")
            assert result["error"] == "Customer not found"
    
    async def test_update_contact_notes_success(self):
        """Test successful contact notes update"""
        tools = CustomerTools("http://localhost:4000")
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"success": True}
            mock_session.post.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            result = await tools.update_contact_notes("+1234567890", "Test notes")
            assert result["success"] is True

@pytest.mark.asyncio
class TestConversationManager:
    """Test suite for ConversationManager"""
    
    async def test_get_conversation_history_empty(self, mock_redis):
        """Test getting empty conversation history"""
        manager = ConversationManager(mock_redis)
        mock_redis.get.return_value = None
        
        history = await manager.get_conversation_history("test-conv")
        assert history == []
    
    async def test_save_conversation_history(self, mock_redis):
        """Test saving conversation history"""
        manager = ConversationManager(mock_redis)
        
        from langchain.schema import HumanMessage, AIMessage
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        
        await manager.save_conversation_history("test-conv", messages)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "conversation:test-conv"
        assert call_args[0][1] == 86400  # 24 hours

@pytest.mark.asyncio
class TestFastAPIIntegration:
    """Test suite for FastAPI integration"""
    
    async def test_chat_endpoint(self):
        """Test the chat API endpoint"""
        from fastapi.testclient import TestClient
        
        with patch('services.ai_orchestrator.agent_service.get_agent_service') as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.chat.return_value = {
                "response": "Hello!",
                "conversation_id": "test-123",
                "timestamp": "2024-01-01T00:00:00"
            }
            mock_get_agent.return_value = mock_agent
            
            app = create_agent_app()
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": "Hi",
                "conversation_id": "test-123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Hello!"
    
    async def test_health_endpoint(self):
        """Test the health check endpoint"""
        from fastapi.testclient import TestClient
        
        with patch('services.ai_orchestrator.agent_service.get_agent_service') as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.health_check.return_value = {"status": "healthy"}
            mock_get_agent.return_value = mock_agent
            
            app = create_agent_app()
            client = TestClient(app)
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

@pytest.mark.asyncio
class TestAgentConfig:
    """Test suite for AgentConfig"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            config = AgentConfig()
            assert config.primary_model == "gpt-4-turbo-preview"
            assert config.fallback_model == "claude-3-sonnet-20240229"
            assert config.max_tokens == 150
            assert config.temperature == 0.7
    
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        env_vars = {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-anthropic",
            "AI_PRIMARY_MODEL": "gpt-3.5-turbo",
            "AI_FALLBACK_MODEL": "claude-3-haiku",
            "AI_MAX_TOKENS": "100",
            "AI_TEMPERATURE": "0.8",
            "REDIS_URL": "redis://test:6379",
            "ELIXIR_API_URL": "http://test:4000"
        }
        
        with patch.dict(os.environ, env_vars):
            config = AgentConfig()
            assert config.openai_api_key == "test-key"
            assert config.anthropic_api_key == "test-anthropic"
            assert config.primary_model == "gpt-3.5-turbo"
            assert config.fallback_model == "claude-3-haiku"
            assert config.max_tokens == 100
            assert config.temperature == 0.8

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
