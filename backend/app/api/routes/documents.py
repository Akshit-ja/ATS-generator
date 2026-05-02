"""
API routes for document operations.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ...database import get_db
from ...db.models import Document
from ...auth.jwt import get_current_active_user
from ...auth.models import User
from ..schemas.documents import DocumentResponse
from ...core.storage import storage
from ..dependencies import verify_resume_ownership

router = APIRouter(prefix="/api/v1", tags=["documents"])

@router.post("/resumes/{resume_id}/documents", response_model=DocumentResponse)
async def upload_document(
    resume_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a document for a specific resume."""
    # Verify resume ownership
    await verify_resume_ownership(resume_id, current_user.id, db)
    
    # Check file type
    content_type = file.content_type
    allowed_types = ["application/pdf", "application/msword", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Supported types: PDF, DOC, DOCX"
        )
    
    try:
        # Upload file to S3
        object_key = await storage.upload_file(file, current_user.id, "document")
        
        # Generate presigned URL (valid for 24 hours)
        presigned_url = storage.generate_presigned_url(object_key)
        expires_at = datetime.now() + timedelta(days=1)
        
        # Get file extension
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        
        # Create document record
        db_document = Document(
            resume_id=resume_id,
            filename=file.filename,
            file_type=file_extension,
            file_path=object_key,
            file_size=file.size,
            storage_type="s3",
            s3_url=presigned_url,
            content_type=content_type,
            expires_at=expires_at
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return db_document
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document details and generate a fresh presigned URL if needed."""
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify ownership through resume
    await verify_resume_ownership(document.resume_id, current_user.id, db)
    
    # Check if URL is expired and regenerate if needed
    if document.storage_type == "s3" and (not document.expires_at or document.expires_at < datetime.now()):
        # Generate new presigned URL
        presigned_url = storage.generate_presigned_url(document.file_path)
        expires_at = datetime.now() + timedelta(days=1)
        
        # Update document
        document.s3_url = presigned_url
        document.expires_at = expires_at
        db.commit()
        db.refresh(document)
    
    return document

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify ownership through resume
    await verify_resume_ownership(document.resume_id, current_user.id, db)
    
    try:
        # Delete from S3 if stored there
        if document.storage_type == "s3":
            await storage.delete_file(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )

@router.get("/resumes/{resume_id}/documents", response_model=List[DocumentResponse])
async def get_resume_documents(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific resume."""
    # Verify resume ownership
    await verify_resume_ownership(resume_id, current_user.id, db)
    
    # Get documents
    documents = db.query(Document).filter(Document.resume_id == resume_id).all()
    
    # Update expired URLs
    now = datetime.now()
    for doc in documents:
        if doc.storage_type == "s3" and (not doc.expires_at or doc.expires_at < now):
            # Generate new presigned URL
            doc.s3_url = storage.generate_presigned_url(doc.file_path)
            doc.expires_at = now + timedelta(days=1)
    
    # Commit any URL updates
    if any(doc.storage_type == "s3" and (not doc.expires_at or doc.expires_at < now) for doc in documents):
        db.commit()
    
    return documents