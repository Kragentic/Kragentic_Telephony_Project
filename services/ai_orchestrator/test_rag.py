"""
Comprehensive tests for the RAG (Retrieval-Augmented Generation) Service
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.ai_orchestrator.rag_service import (
    RAGService,
    RAGConfig,
    DocumentInput,
    SearchQuery,
    create_rag_app
)

class TestRAGConfig:
    """Test configuration for RAG tests"""
    def __init__(self):
        self.pinecone_api_key = "test-pinecone-key"
        self.pinecone_environment = "us-west1-gcp"
        self.pinecone_index_name = "test-knowledge"
        self.openai_api_key = "test-openai-key"
        self.redis_url = "redis://localhost:6379"
        self.chunk_size = 500
        self.chunk_overlap = 100
        self.top_k = 3
        self.cache_ttl = 1800

@pytest.fixture
def mock_pinecone():
    """Mock Pinecone client"""
    mock = MagicMock()
    mock.list_indexes.return_value = ["test-knowledge"]
    mock.describe_index_stats.return_value = {"total_vector_count": 100}
    return mock

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.ping.return_value = True
    mock.get.return_value = None
    mock.setex.return_value = True
    return mock

@pytest.fixture
def rag_config():
    """Test RAG configuration"""
    return TestRAGConfig()

@pytest.fixture
async def rag_service(rag_config, mock_redis):
    """Create test RAG service"""
    with patch('pinecone.init'), \
         patch('pinecone.Index') as mock_index, \
         patch('redis.asyncio.from_url', return_value=mock_redis):
        
        mock_index.return_value.describe_index_stats.return_value = {"total_vector_count": 100}
        
        service = RAGService(rag_config)
        await service.initialize()
        return service

@pytest.mark.asyncio
class TestRAGService:
    """Test suite for RAG Service"""
    
    async def test_initialization(self, rag_config, mock_redis):
        """Test service initialization"""
        with patch('pinecone.init'), \
             patch('pinecone.Index') as mock_index, \
             patch('redis.asyncio.from_url', return_value=mock_redis):
            
            mock_index.return_value.describe_index_stats.return_value = {"total_vector_count": 100}
            
            service = RAGService(rag_config)
            await service.initialize()
            
            assert service.index is not None
            assert service.vector_store is not None
            assert service.redis_client is not None
    
    async def test_add_document(self, rag_service):
        """Test adding a single document"""
        doc_input = DocumentInput(
            content="This is a test document about refund policies.",
            metadata={"category": "policies", "source": "FAQ"},
            doc_type="text",
            source="test"
        )
        
        with patch.object(rag_service.vector_store, 'add_documents') as mock_add:
            mock_add.return_value = None
            
            result = await rag_service.add_document(doc_input)
            
            assert result["status"] == "success"
            assert result["chunks"] > 0
            assert result["doc_id"] is not None
    
    async def test_add_documents_batch(self, rag_service):
        """Test adding multiple documents"""
        documents = [
            DocumentInput(
                content="Document 1 about refunds",
                metadata={"category": "policies"},
                doc_type="text",
                source="test1"
            ),
            DocumentInput(
                content="Document 2 about returns",
                metadata={"category": "policies"},
                doc_type="text",
                source="test2"
            )
        ]
        
        with patch.object(rag_service, 'add_document') as mock_add:
            mock_add.return_value = {"status": "success", "chunks": 2}
            
            result = await rag_service.add_documents_batch(documents)
            
            assert result["total_documents"] == 2
            assert result["successful"] == 2
    
    async def test_search(self, rag_service):
        """Test similarity search"""
        query = SearchQuery(
            query="What is the refund policy?",
            top_k=3
        )
        
        with patch.object(rag_service.vector_store, 'similarity_search') as mock_search:
            mock_search.return_value = [
                Document(
                    page_content="Our refund policy allows returns within 30 days.",
                    metadata={"category": "policies", "score": 0.95}
                ),
                Document(
                    page_content="Returns must be in original condition.",
                    metadata={"category": "policies", "score": 0.85}
                )
            ]
            
            result = await rag_service.search(query)
            
            assert result["status"] == "success"
            assert len(result["results"]) == 2
            assert result["results"][0]["content"] == "Our refund policy allows returns within 30 days."
    
    async def test_get_context(self, rag_service):
        """Test getting context for AI agent"""
        with patch.object(rag_service, 'search') as mock_search:
            mock_search.return_value = {
                "status": "success",
                "results": [
                    {"content": "Refund policy info", "metadata": {"score": 0.95}}
                ]
            }
            
            context = await rag_service.get_context("What is the refund policy?", 3)
            
            assert len(context) == 1
            assert context[0]["content"] == "Refund policy info"
    
    async def test_delete_document(self, rag_service):
        """Test deleting a document"""
        doc_id = "test-doc-123"
        
        result = await rag_service.delete_document(doc_id)
        
        assert result["doc_id"] == doc_id
        assert result["status"] == "success"
    
    async def test_get_stats(self, rag_service):
        """Test getting knowledge base statistics"""
        with patch.object(rag_service.index, 'describe_index_stats') as mock_stats:
            mock_stats.return_value = {"total_vector_count": 150}
            
            stats = await rag_service.get_stats()
            
            assert stats["total_documents"] == 150
            assert stats["status"] == "success"
    
    async def test_health_check_healthy(self, rag_service):
        """Test health check when all services are healthy"""
        with patch.object(rag_service.index, 'describe_index_stats') as mock_stats, \
             patch.object(rag_service.redis_client, 'ping') as mock_ping:
            
            mock_stats.return_value = {"total_vector_count": 100}
            mock_ping.return_value = True
            
            health = await rag_service.health_check()
            
            assert health["status"] == "healthy"
            assert health["total_documents"] == 100
    
    async def test_health_check_unhealthy(self, rag_service):
        """Test health check when services are unhealthy"""
        with patch.object(rag_service.index, 'describe_index_stats') as mock_stats:
            mock_stats.side_effect = Exception("Pinecone connection failed")
            
            health = await rag_service.health_check()
            
            assert health["status"] == "unhealthy"
            assert "error" in health
    
    async def test_cache_integration(self, rag_service):
        """Test Redis caching integration"""
        query = SearchQuery(
            query="Test caching",
            top_k=2
        )
        
        # First call - should cache
        with patch.object(rag_service.vector_store, 'similarity_search') as mock_search:
            mock_search.return_value = [
                Document(page_content="Cached content", metadata={"score": 0.9})
            ]
            
            result1 = await rag_service.search(query)
            assert result1["status"] == "success"
        
        # Second call - should use cache
        with patch.object(rag_service.redis_client, 'get') as mock_get:
            mock_get.return_value = json.dumps({
                "query": "Test caching",
                "results": [{"content": "Cached content", "metadata": {"score": 0.9}}],
                "total_results": 1
            })
            
            result2 = await rag_service.search(query)
            assert result2["status"] == "success"

@pytest.mark.asyncio
class TestFastAPIIntegration:
    """Test suite for FastAPI integration"""
    
    async def test_upload_endpoint(self):
        """Test the upload API endpoint"""
        from fastapi.testclient import TestClient
        
        with patch('services.ai_orchestrator.rag_service.get_rag_service') as mock_get_rag:
            mock_rag = AsyncMock()
            mock_rag.add_document.return_value = {
                "doc_id": "test-doc-123",
                "chunks": 2,
                "status": "success"
            }
            mock_get_rag.return_value = mock_rag
            
            app = create_rag_app()
            client = TestClient(app)
            
            response = client.post("/api/rag/upload", json={
                "content": "Test document content",
                "metadata": {"category": "test"},
                "doc_type": "text",
                "source": "api"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    async def test_search_endpoint(self):
        """Test the search API endpoint"""
        from fastapi.testclient import TestClient
        
        with patch('services.ai_orchestrator.rag_service.get_rag_service') as mock_get_rag:
            mock_rag = AsyncMock()
            mock_rag.search.return_value = {
                "query": "test query",
                "results": [{"content": "test result"}],
                "status": "success"
            }
            mock_get_rag.return_value = mock_rag
            
            app = create_rag_app()
            client = TestClient(app)
            
            response = client.post("/api/rag/search", json={
                "query": "test query",
                "top_k": 3
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    async def test_context_endpoint(self):
        """Test the context API endpoint"""
        from fastapi.testclient import TestClient
        
        with patch('services.ai_orchestrator.rag_service.get_rag_service') as mock_get_rag:
            mock_rag = AsyncMock()
            mock_rag.get_context.return_value = [
                {"content": "context result", "metadata": {"score": 0.9}}
            ]
            mock_get_rag.return_value = mock_rag
            
            app = create_rag_app()
            client = TestClient(app)
            
            response = client.get("/api/rag/context?query=test%20query&top_k=3")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["context"]) == 1

@pytest.mark.asyncio
class TestRAGConfig:
    """Test suite for RAG configuration"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            config = RAGConfig()
            assert config.pinecone_api_key == ""
            assert config.pinecone_environment == "us-west1-gcp"
            assert config.pinecone_index_name == "kragentic-knowledge"
            assert config.openai_api_key == ""
            assert config.chunk_size == 500
            assert config.top_k == 3
    
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        env_vars = {
            "PINECONE_API_KEY": "test-pinecone-key",
            "PINECONE_ENVIRONMENT": "us-east1-gcp",
            "PINECONE_INDEX_NAME": "test-index",
            "OPENAI_API_KEY": "test-openai-key",
            "REDIS_URL": "redis://test:6379",
            "CHUNK_SIZE": "1000",
            "TOP_K": "5"
        }
        
        with patch.dict(os.environ, env_vars):
            config = RAGConfig()
            assert config.pinecone_api_key == "test-pinecone-key"
            assert config.pinecone_environment == "us-east1-gcp"
            assert config.pinecone_index_name == "test-index"
            assert config.openai_api_key == "test-openai-key"
            assert config.chunk_size == 1000
            assert config.top_k == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
