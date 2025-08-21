"""
LangChain AI Agent Service for Kragentic Telephony
Provides conversational AI capabilities with memory and tools
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.manager import CallbackManagerForToolRun

from pydantic import BaseModel, Field
import aiohttp
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentConfig:
    """Configuration for the AI agent"""
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.primary_model = os.getenv("AI_PRIMARY_MODEL", "gpt-4-turbo-preview")
        self.fallback_model = os.getenv("AI_FALLBACK_MODEL", "claude-3-sonnet-20240229")
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "150"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.elixir_api_url = os.getenv("ELIXIR_API_URL", "http://localhost:4000")

class CustomerInfoInput(BaseModel):
    """Input schema for customer info tool"""
    phone_number: str = Field(description="The customer's phone number")

class UpdateNotesInput(BaseModel):
    """Input schema for updating contact notes"""
    phone_number: str = Field(description="The customer's phone number")
    notes: str = Field(description="Notes to add/update for the customer")

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def get_conversation_history(self, conversation_id: str) -> List[BaseMessage]:
        """Retrieve conversation history from Redis"""
        try:
            key = f"conversation:{conversation_id}"
            history_json = await self.redis.get(key)
            if history_json:
                history = json.loads(history_json)
                messages = []
                for msg in history:
                    if msg["type"] == "human":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["type"] == "ai":
                        messages.append(AIMessage(content=msg["content"]))
                return messages
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    async def save_conversation_history(self, conversation_id: str, messages: List[BaseMessage]):
        """Save conversation history to Redis"""
        try:
            key = f"conversation:{conversation_id}"
            history = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({"type": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"type": "ai", "content": msg.content})
            
            await self.redis.setex(
                key, 
                86400,  # 24 hour TTL
                json.dumps(history)
            )
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")

class CustomerTools:
    """Tools for customer information management"""
    
    def __init__(self, elixir_api_url: str):
        self.elixir_api_url = elixir_api_url
    
    async def get_customer_info(self, phone_number: str) -> Dict[str, Any]:
        """Get customer information by phone number"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.elixir_api_url}/api/contacts/by_phone/{phone_number}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return {"error": "Customer not found"}
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error getting customer info: {e}")
            return {"error": str(e)}
    
    async def update_contact_notes(self, phone_number: str, notes: str) -> Dict[str, Any]:
        """Update contact notes"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.elixir_api_url}/api/contacts/update_notes"
                data = {"phone_number": phone_number, "notes": notes}
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error updating contact notes: {e}")
            return {"error": str(e)}

class AIAgentService:
    """Main AI agent service with LangChain integration"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.redis_client = None
        self.conversation_manager = None
        self.customer_tools = None
        self.agent_executor = None
        
    async def initialize(self):
        """Initialize the AI agent service"""
        try:
            # Initialize Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            self.conversation_manager = ConversationManager(self.redis_client)
            self.customer_tools = CustomerTools(self.config.elixir_api_url)
            
            # Initialize LLM
            self.llm = self._initialize_llm()
            
            # Create tools
            tools = self._create_tools()
            
            # Create agent
            self.agent_executor = self._create_agent(tools)
            
            logger.info("AI Agent service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI agent service: {e}")
            raise
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model"""
        if self.config.openai_api_key:
            return ChatOpenAI(
                model=self.config.primary_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                openai_api_key=self.config.openai_api_key
            )
        elif self.config.anthropic_api_key:
            return ChatAnthropic(
                model=self.config.fallback_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                anthropic_api_key=self.config.anthropic_api_key
            )
        else:
            raise ValueError("No API keys provided for AI models")
    
    def _create_tools(self) -> List[Tool]:
        """Create available tools for the agent"""
        
        # Customer info tool
        customer_info_tool = StructuredTool.from_function(
            func=self._get_customer_info_tool,
            name="get_customer_info",
            description="Get customer information by phone number",
            args_schema=CustomerInfoInput
        )
        
        # Update notes tool
        update_notes_tool = StructuredTool.from_function(
            func=self._update_contact_notes_tool,
            name="update_contact_notes",
            description="Update notes for a customer contact",
            args_schema=UpdateNotesInput
        )
        
        return [customer_info_tool, update_notes_tool]
    
    def _create_agent(self, tools: List[Tool]) -> AgentExecutor:
        """Create the LangChain agent"""
        
        system_prompt = """You are a helpful AI assistant for Kragentic Telephony. 
        You are professional, friendly, and concise in your responses.
        Always maintain context from previous messages and use the available tools to help customers.
        
        Key guidelines:
        - Be concise and clear in responses
        - Use the customer info tool when phone number is provided
        - Update contact notes when relevant information is shared
        - Maintain conversation context
        - If you don't know something, be honest about it
        - Always be helpful and professional"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )
    
    async def _get_customer_info_tool(self, phone_number: str) -> str:
        """Tool to get customer information"""
        customer_info = await self.customer_tools.get_customer_info(phone_number)
        return json.dumps(customer_info, indent=2)
    
    async def _update_contact_notes_tool(self, phone_number: str, notes: str) -> str:
        """Tool to update contact notes"""
        result = await self.customer_tools.update_contact_notes(phone_number, notes)
        return json.dumps(result, indent=2)
    
    async def chat(self, message: str, conversation_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Process a chat message and return response"""
        try:
            # Get conversation history
            history = await self.conversation_manager.get_conversation_history(conversation_id)
            
            # Create memory with history
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Add history to memory
            for msg in history:
                if isinstance(msg, HumanMessage):
                    memory.chat_memory.add_user_message(msg.content)
                elif isinstance(msg, AIMessage):
                    memory.chat_memory.add_ai_message(msg.content)
            
            # Add current message
            memory.chat_memory.add_user_message(message)
            
            # Prepare inputs
            inputs = {
                "input": message,
                "chat_history": memory.chat_memory.messages
            }
            
            # Add phone number to inputs if provided
            if phone_number:
                inputs["phone_number"] = phone_number
            
            # Run agent
            response = await self.agent_executor.ainvoke(inputs)
            
            # Save updated conversation
            updated_history = memory.chat_memory.messages
            await self.conversation_manager.save_conversation_history(
                conversation_id, 
                updated_history
            )
            
            return {
                "response": response["output"],
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request. Please try again.",
                "error": str(e),
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history"""
        try:
            key = f"conversation:{conversation_id}"
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for display"""
        try:
            history = await self.conversation_manager.get_conversation_history(conversation_id)
            return [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                    "timestamp": datetime.utcnow().isoformat()
                }
                for msg in history
            ]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the AI agent service"""
        try:
            # Test Redis connection
            await self.redis_client.ping()
            
            # Test LLM
            test_response = await self.llm.ainvoke("Hello")
            
            # Test customer tools
            test_customer = await self.customer_tools.get_customer_info("+1234567890")
            
            return {
                "status": "healthy",
                "redis": "connected",
                "llm": "responsive",
                "customer_tools": "accessible",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global instance
_agent_service = None

async def get_agent_service() -> AIAgentService:
    """Get or create the AI agent service instance"""
    global _agent_service
    if _agent_service is None:
        config = AgentConfig()
        _agent_service = AIAgentService(config)
        await _agent_service.initialize()
    return _agent_service

# FastAPI integration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    phone_number: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

def create_agent_app() -> FastAPI:
    """Create FastAPI app for the agent service"""
    app = FastAPI(title="AI Agent Service", version="1.0.0")
    
    @app.on_event("startup")
    async def startup_event():
        await get_agent_service()
    
    @app.post("/api/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        agent = await get_agent_service()
        result = await agent.chat(
            request.message,
            request.conversation_id,
            request.phone_number
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
    
    @app.get("/api/chat/history/{conversation_id}")
    async def get_history(conversation_id: str):
        agent = await get_agent_service()
        history = await agent.get_conversation_history(conversation_id)
        return {"history": history}
    
    @app.delete("/api/chat/clear/{conversation_id}")
    async def clear_conversation(conversation_id: str):
        agent = await get_agent_service()
        success = await agent.clear_conversation(conversation_id)
        return {"success": success}
    
    @app.get("/health")
    async def health_check():
        agent = await get_agent_service()
        return await agent.health_check()
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_agent_app()
    uvicorn.run(app, host="0.0.0.0", port=8002)
