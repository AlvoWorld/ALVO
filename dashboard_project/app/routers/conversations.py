"""
Conversations API Router.

Handles conversation history and search.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.ConversationResponse)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db)
):
    """Log a conversation message."""
    # Verify agent exists
    agent = db.query(models.Agent).filter(
        models.Agent.id == conversation.agent_id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db_conversation = models.Conversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


@router.get("/", response_model=schemas.ConversationSearchResponse)
async def list_conversations(
    agent_id: int = None,
    session_id: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List conversations with optional filters."""
    query = db.query(models.Conversation)

    if agent_id:
        query = query.filter(models.Conversation.agent_id == agent_id)
    if session_id:
        query = query.filter(models.Conversation.session_id == session_id)

    total = query.count()
    conversations = query.order_by(
        models.Conversation.created_at.desc()
    ).offset(skip).limit(limit).all()

    return schemas.ConversationSearchResponse(
        results=conversations,
        total=total,
        query=""
    )


@router.post("/search", response_model=schemas.ConversationSearchResponse)
async def search_conversations(
    search: schemas.ConversationSearchRequest,
    db: Session = Depends(get_db)
):
    """Search across conversation content."""
    query = db.query(models.Conversation).filter(
        models.Conversation.content.ilike(f"%{search.query}%")
    )

    if search.agent_id:
        query = query.filter(models.Conversation.agent_id == search.agent_id)
    if search.session_id:
        query = query.filter(models.Conversation.session_id == search.session_id)

    total = query.count()
    results = query.order_by(
        models.Conversation.created_at.desc()
    ).limit(search.limit).all()

    return schemas.ConversationSearchResponse(
        results=results,
        total=total,
        query=search.query
    )


@router.get("/{conversation_id}", response_model=schemas.ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation by ID."""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
