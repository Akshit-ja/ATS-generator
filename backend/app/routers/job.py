from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..services.job_analyzer import JobAnalyzer
from ..auth.jwt import get_current_active_user
from ..db.models import User
from ..middleware.rate_limiter import rate_limit

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

@router.post("/analyze")
@rate_limit(requests=5, period=60)  # 5 requests per minute
async def analyze_job(
    job_description: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a job description to extract key information"""
    job_analyzer = JobAnalyzer(db)
    
    # Mock implementation for job analysis
    skills = job_analyzer.extract_skills(job_description.get("description", ""))
    experience_level = job_analyzer.determine_experience_level(job_description.get("description", ""))
    
    return {
        "skills": skills,
        "experience_level": experience_level,
        "job_id": job_description.get("id", "unknown")
    }

@router.post("/match")
@rate_limit(requests=3, period=60)  # 3 requests per minute
async def match_resume_to_job(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Match a resume to a job description and provide a compatibility score"""
    # Mock implementation for resume-job matching
    return {
        "match_score": 85,
        "missing_skills": ["Docker", "Kubernetes"],
        "matching_skills": ["Python", "FastAPI", "SQL"],
        "recommendations": "Consider adding Docker experience to your resume"
    }