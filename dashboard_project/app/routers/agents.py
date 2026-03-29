"""
Agents API Router.

Handles agent CRUD operations and status management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.AgentResponse)
async def create_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent configuration."""
    # Check for duplicate name
    existing = db.query(models.Agent).filter(
        models.Agent.name == agent.name
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Agent name already exists")

    db_agent = models.Agent(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    return db_agent


@router.get("/", response_model=schemas.AgentListResponse)
async def list_agents(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all agents."""
    query = db.query(models.Agent)
    if active_only:
        query = query.filter(models.Agent.is_active == True)

    total = query.count()
    agents = query.offset(skip).limit(limit).all()

    return schemas.AgentListResponse(agents=agents, total=total)


@router.get("/{agent_id}", response_model=schemas.AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific agent by ID."""
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=schemas.AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: schemas.AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update an agent configuration."""
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Delete an agent."""
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()

    return {"message": "Agent deleted", "id": agent_id}


@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific agent."""
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    conversation_count = db.query(models.Conversation).filter(
        models.Conversation.agent_id == agent_id
    ).count()

    knowledge_count = db.query(models.KnowledgeBase).filter(
        models.KnowledgeBase.agent_id == agent_id
    ).count()

    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "conversation_count": conversation_count,
        "knowledge_entries": knowledge_count,
        "is_active": agent.is_active,
    }
