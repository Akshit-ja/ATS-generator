from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..auth.jwt import get_current_active_user
from ..db.models import User, EndpointType
from ..middleware.rate_limiter import rate_limit
from ..services.token_tracker import TokenTracker

router = APIRouter(
    prefix="/generate",
    tags=["generate"],
    responses={404: {"description": "Not found"}},
)

@router.post("/cover-letter")
@rate_limit(requests=2, period=60)  # 2 requests per minute
async def generate_cover_letter(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a cover letter based on resume and job description"""
    # Mock OpenAI response for demonstration
    mock_openai_response = {
        "model": "gpt-3.5-turbo",
        "usage": {
            "prompt_tokens": 300,
            "completion_tokens": 200,
            "total_tokens": 500
        }
    }
    
    # Track token usage
    token_tracker = TokenTracker(db)
    token_tracker.track_usage_from_response(
        response=mock_openai_response,
        user_id=current_user.id,
        endpoint_type=EndpointType.COVER_LETTER_GENERATION,
        job_id=data.get("job_id")
    )
    
    return {
        "cover_letter": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {data.get('job_title', 'position')} at {data.get('company', 'your company')}...",
        "tokens_used": mock_openai_response["usage"]["total_tokens"]
    }

@router.post("/interview-questions")
@rate_limit(requests=3, period=60)  # 3 requests per minute
async def generate_interview_questions(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate potential interview questions based on job description"""
    # Mock OpenAI response for demonstration
    mock_openai_response = {
        "model": "gpt-3.5-turbo",
        "usage": {
            "prompt_tokens": 200,
            "completion_tokens": 150,
            "total_tokens": 350
        }
    }
    
    # Track token usage
    token_tracker = TokenTracker(db)
    token_tracker.track_usage_from_response(
        response=mock_openai_response,
        user_id=current_user.id,
        endpoint_type=EndpointType.INTERVIEW_PREP,
        job_id=data.get("job_id")
    )
    
    return {
        "questions": [
            "Tell me about your experience with Python and FastAPI.",
            "How do you handle challenging deadlines?",
            "Describe a situation where you had to learn a new technology quickly."
        ],
        "tokens_used": mock_openai_response["usage"]["total_tokens"]
    }