"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentBase(BaseModel):
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    original_filename: str
    content_hash: str
    upload_date: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# ============================================================================
# Agent Schemas
# ============================================================================

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: Optional[str] = None
    is_active: bool = True


class AgentCreate(AgentBase):
    config_json: Optional[str] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    config_json: Optional[str] = None


class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int


# ============================================================================
# Conversation Schemas
# ============================================================================

class ConversationCreate(BaseModel):
    agent_id: int
    session_id: str
    role: str
    content: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None


class ConversationResponse(ConversationCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSearchRequest(BaseModel):
    query: str
    agent_id: Optional[int] = None
    session_id: Optional[str] = None
    limit: int = Field(default=20, le=100)


class ConversationSearchResponse(BaseModel):
    results: List[ConversationResponse]
    total: int
    query: str


# ============================================================================
# Knowledge Base Schemas
# ============================================================================

class KnowledgeBaseCreate(BaseModel):
    agent_id: Optional[int] = None
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeBaseResponse(KnowledgeBaseCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseSearchRequest(BaseModel):
    query: str
    agent_id: Optional[int] = None
    category: Optional[str] = None
    limit: int = Field(default=10, le=50)


# ============================================================================
# LLM Request Log Schemas
# ============================================================================

class LLMRequestLogResponse(BaseModel):
    id: int
    model: str
    status_code: int
    tokens_used: Optional[int]
    latency_ms: int
    was_rate_limited: bool
    retry_count: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LLMStatsResponse(BaseModel):
    total_requests: int
    total_retries: int
    rate_limit_hits: int
    avg_latency_ms: float
    requests_by_model: Dict[str, int]
