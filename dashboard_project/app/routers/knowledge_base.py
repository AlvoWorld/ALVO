"""
Knowledge Base API Router.

Handles knowledge base entries for agents.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.KnowledgeBaseResponse)
async def create_entry(
    entry: schemas.KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new knowledge base entry."""
    # Verify agent exists if agent_id provided
    if entry.agent_id:
        agent = db.query(models.Agent).filter(
            models.Agent.id == entry.agent_id
        ).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

    db_entry = models.KnowledgeBase(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return db_entry


@router.get("/", response_model=list[schemas.KnowledgeBaseResponse])
async def list_entries(
    agent_id: int = None,
    category: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List knowledge base entries with optional filters."""
    query = db.query(models.KnowledgeBase)

    if agent_id:
        query = query.filter(models.KnowledgeBase.agent_id == agent_id)
    if category:
        query = query.filter(models.KnowledgeBase.category == category)

    return query.offset(skip).limit(limit).all()


@router.get("/{entry_id}", response_model=schemas.KnowledgeBaseResponse)
async def get_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific knowledge base entry."""
    entry = db.query(models.KnowledgeBase).filter(
        models.KnowledgeBase.id == entry_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.put("/{entry_id}", response_model=schemas.KnowledgeBaseResponse)
async def update_entry(
    entry_id: int,
    entry_update: schemas.KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a knowledge base entry."""
    entry = db.query(models.KnowledgeBase).filter(
        models.KnowledgeBase.id == entry_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)

    return entry


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Delete a knowledge base entry."""
    entry = db.query(models.KnowledgeBase).filter(
        models.KnowledgeBase.id == entry_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()

    return {"message": "Entry deleted", "id": entry_id}


@router.post("/search", response_model=list[schemas.KnowledgeBaseResponse])
async def search_entries(
    search: schemas.KnowledgeBaseSearchRequest,
    db: Session = Depends(get_db)
):
    """Search knowledge base entries."""
    query = db.query(models.KnowledgeBase).filter(
        or_(
            models.KnowledgeBase.title.ilike(f"%{search.query}%"),
            models.KnowledgeBase.content.ilike(f"%{search.query}%"),
            models.KnowledgeBase.tags.ilike(f"%{search.query}%"),
        )
    )

    if search.agent_id:
        query = query.filter(models.KnowledgeBase.agent_id == search.agent_id)
    if search.category:
        query = query.filter(models.KnowledgeBase.category == search.category)

    return query.limit(search.limit).all()
