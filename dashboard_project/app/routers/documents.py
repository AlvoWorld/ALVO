"""
Documents API Router.

Handles document upload, retrieval, and management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import hashlib
import os

from ..database import get_db
from .. import models, schemas

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document to the knowledge base."""
    # Read file content
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()

    # Check for duplicate
    existing = db.query(models.Document).filter(
        models.Document.content_hash == content_hash
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Document already exists")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{content_hash}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    doc = models.Document(
        filename=file.filename,
        original_filename=file.filename,
        file_type=file.content_type,
        file_size=len(content),
        content_hash=content_hash,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/", response_model=schemas.DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all uploaded documents."""
    total = db.query(models.Document).count()
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return schemas.DocumentListResponse(documents=documents, total=total)


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document."""
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from disk
    file_path = os.path.join(UPLOAD_DIR, f"{doc.content_hash}_{doc.filename}")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(doc)
    db.commit()

    return {"message": "Document deleted", "id": document_id}
