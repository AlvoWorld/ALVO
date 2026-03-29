"""
SQLAlchemy ORM models for the dashboard database.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Document(Base):
    """Uploaded document model."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    content_hash = Column(String(64), unique=True, index=True)
    extracted_text = Column(Text)
    upload_date = Column(DateTime, server_default=func.now())
    metadata_json = Column(Text)  # JSON metadata

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


class Agent(Base):
    """Agent configuration model."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    agent_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    config_json = Column(Text)  # JSON configuration
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    conversations = relationship("Conversation", back_populates="agent")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}')>"


class Conversation(Base):
    """Conversation history model."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    session_id = Column(String(100), index=True)
    role = Column(String(20))  # 'system', 'user', 'assistant'
    content = Column(Text)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    agent = relationship("Agent", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, role='{self.role}')>"


class KnowledgeBase(Base):
    """Knowledge base entries for agents."""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    title = Column(String(255))
    content = Column(Text)
    category = Column(String(100))
    tags = Column(String(500))  # Comma-separated tags
    embedding_id = Column(String(100))  # Reference to vector store
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}')>"


class LLMRequestLog(Base):
    """Log of LLM API requests for monitoring."""
    __tablename__ = "llm_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100))
    status_code = Column(Integer)
    tokens_used = Column(Integer)
    latency_ms = Column(Integer)
    was_rate_limited = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<LLMRequestLog(id={self.id}, model='{self.model}')>"
