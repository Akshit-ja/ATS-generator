from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import inspect
import logging
import os
from ...services.resume_parser import ResumeParser
from ...services.resume_matcher import ResumeMatcher
from ...auth.models import User
from ...auth.jwt import get_current_active_user, get_optional_current_user
from ..dependencies import rate_limit_dependency, verify_resume_ownership
from sqlalchemy.orm import Session
from ...database import get_db
from ...db.models import Resume
from ...routers import resume as legacy_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["resumes"])
resume_parser = ResumeParser()
resume_matcher = ResumeMatcher()

class ResumeBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: str

class ParsedResumeResponse(BaseModel):
    text: str
    name: Optional[str] = None
    email: Optional[str] = None
    sections: List[str] = []

class MatchScoreRequest(BaseModel):
    resume_text: str
    job_description: str

class MatchScoreResponse(BaseModel):
    overall_match_score: int
    breakdown: Dict[str, float]
    missing_critical_keywords: List[str]

@router.post("/resumes/generate")
async def generate_resume_content(
    resume_data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_current_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Generate resume content for the provided resume data.
    """
    resume_service = legacy_resume.ResumeService()
    try:
        job_description = resume_data.get("job_description", "")
        template = resume_data.get("template", "modern")
        result = resume_service.generate_resume_content(resume_data, job_description, template)
        if inspect.isawaitable(result):
            result = await result
        return result
    except Exception as e:
        logger.exception("Resume generation failed")
        raise HTTPException(status_code=500, detail="Error generating resume")

@router.post("/resumes/cover-letter")
async def generate_cover_letter(
    cover_letter_request: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_current_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Generate a cover letter based on resume data and job description.
    """
    resume_service = legacy_resume.ResumeService()
    try:
        resume_data = cover_letter_request.get("resume_data", {})
        job_description = cover_letter_request.get("job_description", "")
        style = cover_letter_request.get("template", cover_letter_request.get("style", "professional"))
        result = resume_service.generate_cover_letter(resume_data, job_description, style)
        if inspect.isawaitable(result):
            result = await result
        return result
    except Exception as e:
        logger.exception("Cover letter generation failed")
        raise HTTPException(status_code=500, detail="Error generating cover letter")

@router.post("/resumes/match-score")
async def match_resume_to_job_v2(
    match_request: MatchScoreRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Calculate match score between resume and job description.
    """
    matcher = legacy_resume.ResumeMatcher()
    try:
        return matcher.match_resume_to_job(match_request.resume_text, match_request.job_description)
    except Exception as e:
        logger.exception("Resume matching failed")
        raise HTTPException(status_code=500, detail="Error matching resume to job")

@router.post("/parse", response_model=ParsedResumeResponse)
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Parse a resume file and extract structured information
    """
    # Check file extension
    allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Save file temporarily
    file_content = await file.read()
    
    # Parse resume
    parser = ResumeParser()
    try:
        result = parser.parse(file_content, file_ext)
        return ParsedResumeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-score", response_model=MatchScoreResponse)
async def match_resume_to_job(
    match_request: MatchScoreRequest,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Calculate match score between resume and job description
    """
    matcher = ResumeMatcher()
    try:
        result = matcher.calculate_match_score(match_request.resume_text, match_request.job_description)
        return MatchScoreResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resumes/", response_model=ResumeResponse)
async def create_resume(
    resume: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Create a new resume for the current user
    """
    db_resume = Resume(
        **resume.model_dump(),
        user_id=current_user.id
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency()),
    resume: Resume = Depends(verify_resume_ownership)
):
    """Get a resume by ID (only if owned by current user)"""
    return resume
