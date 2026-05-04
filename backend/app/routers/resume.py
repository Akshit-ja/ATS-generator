from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..services.resume_service import ResumeService
from ..services.resume_matcher import ResumeMatcher
from ..auth.jwt import get_current_active_user
from ..db.models import User
from ..middleware.rate_limiter import rate_limit

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
@rate_limit(requests=5, period=60)  # 5 requests per minute
async def create_resume(
    resume_data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new resume"""
    resume_service = ResumeService(db)
    return resume_service.create_resume(resume_data)

@router.get("/{resume_id}")
@rate_limit(requests=10, period=60)  # 10 requests per minute
async def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a resume by ID"""
    resume_service = ResumeService(db)
    resume = resume_service.get_resume(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume

@router.post("/generate")
@rate_limit(requests=2, period=60)  # 2 AI generations per minute
async def generate_ai_resume(
    user_data: Dict,
    job_description: str,
    job_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate an AI-enhanced resume"""
    resume_service = ResumeService(db)
    return resume_service.generate_ai_resume(
        user_data=user_data,
        job_description=job_description,
        user_id=current_user.id,
        job_id=job_id
    )
