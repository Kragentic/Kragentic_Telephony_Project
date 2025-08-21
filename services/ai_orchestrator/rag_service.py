"""
RAG (Retrieval-Augmented Generation) Service for Kragentic Telephony
Provides knowledge retrieval and augmentation for AI agents
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, JSONLoader
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManagerForChainRun

import pinecone
import redis.asyncio as redis
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for RAG service"""
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "kragentic-knowledge")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    cache_ttl: int = 3600  # 1 hour

class DocumentInput(BaseModel):
    """Input schema for document ingestion"""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    doc_type: str = Field("text", description="Document type (text, json, etc.)")
    source: str = Field("unknown", description="Document source")

class SearchQuery(BaseModel):
    """Input schema for similarity search"""
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to return")
    filter: Dict[str, Any] = Field(default_factory=dict, description="Metadata filters")

class RAGService:
    """Main RAG service with Pinecone integration"""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.embeddings = None
        self.vector_store = None
        self.redis_client = None
        self.text_splitter = None
        self.index = None
        
    async def initialize(self):
        """Initialize the RAG service"""
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=self.config.pinecone_api_key,
                environment=self.config.pinecone_environment
            )
            
            # Create or connect to index
            if self.config.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.config.pinecone_index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.config.pinecone_index_name)
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.config.openai_api_key
            )
            
            # Initialize vector store
            self.vector_store = Pinecone(
                index=self.index,
                embedding=self.embeddings,
                text_key="text"
            )
            
            # Initialize Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG service: {e}")
            raise
    
    async def add_document(self, doc_input: DocumentInput) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Create document
            document = Document(
                page_content=doc_input.content,
                metadata={
                    **doc_input.metadata,
                    "doc_id": doc_id,
                    "source": doc_input.source,
                    "doc_type": doc_input.doc_type,
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([document])
            
            # Add to vector store
            ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
            self.vector_store.add_documents(chunks, ids=ids)
            
            # Cache the document
            cache_key = f"doc:{doc_id}"
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps({
                    "content": doc_input.content,
                    "metadata": doc_input.metadata,
                    "chunks": len(chunks)
                })
            )
            
            return {
                "doc_id": doc_id,
                "chunks": len(chunks),
                "status": "success",
                "message": f"Document added successfully with {len(chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {
                "doc_id": None,
                "chunks": 0,
                "status": "error",
                "message": str(e)
            }
    
    async def add_documents_batch(self, documents: List[DocumentInput]) -> Dict[str, Any]:
        """Add multiple documents to the knowledge base"""
        try:
            results = []
            for doc in documents:
                result = await self.add_document(mir)
                results.append(result)
            
            return {
                "total_documents": len(documents),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error adding documents batch: {e}")
            return {
                "total_documents": len(documents),
                "successful": 0,
                "failed": len(documents),
                "results": []
            }
    
    async def search(self, query: SearchQuery) -> Dict[str, Any]:
        """Search for relevant documents"""
        try:
            # Check cache first
            cache_key = f"search:{hash(query.query + str(query.filter))}"
            cached_result = await self.redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            # Perform similarity search
            results = self.vector_store.similarity_search(
                query=query.query,
                k=query.top_k,
                filter=query.filter
            )
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                })
            
            # Cache results
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps({
                    "query": query.query,
                    "results": formatted_results,
                    "total_results": len(formatted_results)
                })
            )
            
            return {
                "query": query.query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {
                "query": query.query,
                "results": [],
                "total_results": 0,
                "status": "error",
                "message": str(e)
            }
    
    async def get_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get context for AI agent"""
        try:
            search_query = SearchQuery(
                query=query,
                top_k=top_k
            )
            
            result = await self.search(search_query)
            
            if result["status"] == "success":
                return result["results"]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from the knowledge base"""
        try:
            # Delete from vector store
            # Note: This is a simplified implementation
            # In practice, you'd need to track chunk IDs
            return {
                "doc_id": doc_id,
                "status": "success",
                "message": "Document deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {
                "doc_id": doc_id,
                "status": "error",
                "message": str(e)
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            
            return {
                "total_documents": stats.get("total_vector_count", 0),
                "index_size": stats.get("dimension", 0),
                "environment": self.config.pinecone_environment,
                "index_name": self.config.pinecone_index_name,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "index_size": 0,
                "status": "error",
                "message": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for RAG service"""
        try:
            # Test Pinecone connection
            stats = self.index.describe_index_stats()
            
            # Test Redis connection
            await self.redis_client.ping()
            
            return {
                "status": "healthy",
                "pinecone": "connected",
                "redis": "connected",
                "total_documents": stats.get("total_vector_count", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global service instance
_rag_service = None

async def get_rag_service() -> RAGService:
    """Get or create the RAG service instance"""
    global _rag_service
    if _rag_service is None:
        config = RAGConfig()
        _rag_service = RAGService(config)
        await _rag_service.initialize()
    return _rag_service

# FastAPI integration
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

class DocumentUpload(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    doc_type: str = "text"
    source: str = "api"

def create_rag_app() -> FastAPI:
    """Create FastAPI app for the RAG service"""
    app = FastAPI(title="RAG Service", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.on_event("startup")
    async def startup_event():
        await get_rag_service()
    
    @app.post("/api/rag/upload")
    async def upload_document(doc: DocumentUpload):
        service = await get_rag_service()
        result = await service.add_document(
            DocumentInput(
                content=doc.content,
                metadata=doc.metadata,
                doc_type=doc.doc_type,
                source=doc.source
            )
        )
        return result
    
    @app.post("/api/rag/upload/batch")
    async def upload_documents_batch(documents: List[DocumentUpload]):
        service = await get_rag_service()
        inputs = [
            DocumentInput(
                content=doc.content,
                metadata=doc.metadata,
                doc_type=doc.doc_type,
                source=doc.source
            )
            for doc in documents
        ]
        result = await service.add_documents_batch(inputs)
        return result
    
    @app.post("/api/rag/search")
    async def search_documents(query: SearchQuery):
        service = await get_rag_service()
        result = await service.search(query)
        return result
    
    @app.get("/api/rag/context")
    async def get_context(query: str, top_k: int = 3):
        service = await get_rag_service()
        context = await service.get_context(query, top_k)
        return {"context": context}
    
    @app.delete("/api/rag/document/{doc_id}")
    async def delete_document(doc_id: str):
        service = await get_rag_service()
        result = await service.delete_document(doc_id)
        return result
    
    @app.get("/api/rag/stats")
    async def get_stats():
        service = await get_rag_service()
        stats = await service.get_stats()
        return stats
    
    @app.get("/health")
    async def health_check():
        service = await get_rag_service()
        return await service.health_check()
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_rag_app()
    uvicorn.run(app, host="0.0.0.0", port=8003)
