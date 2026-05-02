from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..database import get_db
from ..auth.jwt import get_current_active_user
from ..models import User
from ..services.interview_service import InterviewService
from ..middleware.rate_limiter import rate_limit
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1",
    tags=["interview-questions"],
    responses={404: {"description": "Not found"}},
)

class UserProfileItem(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str
    description: str

class UserProfile(BaseModel):
    name: str
    email: str
    skills: List[str]
    work_history: List[UserProfileItem]
    education: List[Dict[str, str]]

class InterviewRequest(BaseModel):
    job_description: str
    user_profile: UserProfile

class InterviewResponse(BaseModel):
    behavioral_questions: List[Dict[str, Any]]
    technical_questions: List[Dict[str, Any]]
    company_questions: List[Dict[str, Any]]

@router.post("/interview-questions")
@rate_limit(rate_limit=2, burst_limit=1)  # 2 requests per minute, 1 burst request
async def get_interview_questions(
    fastapi_request: Request,
    request: InterviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> InterviewResponse:
    """
    Generate interview questions based on user's career profile and target role.
    """
    try:
        # Create InterviewService instance
        interview_service = InterviewService(db)
        
        # Generate interview questions using service
        questions = interview_service.generate_interview_questions(
            user_id=current_user.id,
            job_description=request.job_description,
            user_profile=request.user_profile.dict()
        )
        
        return InterviewResponse(
            behavioral_questions=questions["behavioral_questions"],
            technical_questions=questions["technical_questions"],
            company_questions=questions["company_questions"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating interview questions: {str(e)}"
        )