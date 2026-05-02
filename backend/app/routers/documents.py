from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..auth.jwt import get_current_active_user
from ..db.models import User
from ..middleware.rate_limiter import rate_limit

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload")
@rate_limit(requests=10, period=60)  # 10 requests per minute
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a document (resume, cover letter, etc.)"""
    # Mock implementation for document upload
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "user_id": current_user.id,
        "status": "uploaded"
    }

@router.get("/")
@rate_limit(requests=20, period=60)  # 20 requests per minute
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all documents for the current user"""
    # Mock implementation for document listing
    return [
        {
            "id": "doc1",
            "filename": "resume.pdf",
            "type": "resume",
            "uploaded_at": "2023-06-15T10:30:00Z"
        },
        {
            "id": "doc2",
            "filename": "cover_letter.docx",
            "type": "cover_letter",
            "uploaded_at": "2023-06-16T14:45:00Z"
        }
    ]