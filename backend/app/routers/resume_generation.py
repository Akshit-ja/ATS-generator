"""
Resume generation router with OpenAI integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from ..database import get_db
from ..auth.jwt import get_current_active_user
from ..models import User
from ..services.multi_ai_service import MultiAIService
from ..services.token_tracker import TokenTracker
from ..middleware.rate_limiter import rate_limit

router = APIRouter(
    prefix="/api/v1",
    tags=["resume-generation"],
    responses={404: {"description": "Not found"}},
)

class WorkExperienceItem(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str
    description: str

class EducationItem(BaseModel):
    degree: str
    major: str
    university: str
    year: str

class UserProfileData(BaseModel):
    name: str
    email: str
    skills: List[str]
    work_history: List[WorkExperienceItem]
    education: List[EducationItem]

class ResumeGenerationRequest(BaseModel):
    job_description: str
    user_profile: UserProfileData

class ResumeResponse(BaseModel):
    professional_summary: str
    technical_skills: str
    professional_experience: str
    education: str
    additional_skills: str
    match_score: Dict[str, Any]

@router.post("/generate-resume", response_model=ResumeResponse)
@rate_limit(rate_limit=5, burst_limit=2)  # 5 requests per minute
async def generate_resume(
    fastapi_request: Request,
    request: ResumeGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a tailored resume using OpenAI based on job description and user profile
    """
    try:
        ai_service = MultiAIService()
        
        # Convert Pydantic model to dict
        user_profile_dict = request.user_profile.dict()
        
        # Generate resume content using AI
        resume_sections = ai_service.generate_resume_content(
            user_profile=user_profile_dict,
            job_description=request.job_description
        )
        
        # Generate full resume text for matching
        full_resume = "\n\n".join([
            f"## {section.replace('_', ' ').title()}\n{content}"
            for section, content in resume_sections.items()
        ])
        
        # Calculate job match score
        match_score = ai_service.calculate_job_match_score(
            resume_content=full_resume,
            job_description=request.job_description
        )
        
        return ResumeResponse(
            professional_summary=resume_sections.get("professional_summary", ""),
            technical_skills=resume_sections.get("technical_skills", ""),
            professional_experience=resume_sections.get("professional_experience", ""),
            education=resume_sections.get("education", ""),
            additional_skills=resume_sections.get("additional_skills", ""),
            match_score=match_score
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
        )

@router.post("/enhance-resume-section")
@rate_limit(rate_limit=10, burst_limit=5)  # 10 requests per minute
async def enhance_resume_section(
    fastapi_request: Request,
    section_content: str,
    section_type: str,
    job_keywords: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enhance a specific resume section using OpenAI
    """
    try:
        ai_service = MultiAIService()
        
        enhanced_content = ai_service.enhance_resume_section(
            section_content=section_content,
            section_type=section_type,
            job_keywords=job_keywords
        )
        
        return {"enhanced_content": enhanced_content}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enhancing resume section: {str(e)}"
        )

@router.post("/analyze-job-match")
@rate_limit(rate_limit=10, burst_limit=5)  # 10 requests per minute  
async def analyze_job_match(
    fastapi_request: Request,
    resume_content: str,
    job_description: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze how well a resume matches a job description
    """
    try:
        ai_service = MultiAIService()
        
        match_analysis = ai_service.calculate_job_match_score(
            resume_content=resume_content,
            job_description=job_description
        )
        
        return match_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing job match: {str(e)}"
        )