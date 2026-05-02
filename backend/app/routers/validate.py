from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..auth.jwt import get_current_active_user
from ..db.models import User, EndpointType
from ..middleware.rate_limiter import rate_limit
from ..services.token_tracker import TokenTracker
from ..services.ats_validator import ATSValidator

router = APIRouter(
    prefix="/validate",
    tags=["validate"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ats")
@rate_limit(requests=5, period=60)  # 5 requests per minute
async def validate_ats(
    data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Validate a resume against ATS systems"""
    # Mock implementation for ATS validation
    validator = ATSValidator()
    
    # Mock OpenAI response for demonstration
    mock_openai_response = {
        "model": "gpt-3.5-turbo",
        "usage": {
            "prompt_tokens": 250,
            "completion_tokens": 100,
            "total_tokens": 350
        }
    }
    
    # Track token usage
    token_tracker = TokenTracker(db)
    token_tracker.track_usage_from_response(
        response=mock_openai_response,
        user_id=current_user.id,
        endpoint_type=EndpointType.ATS_VALIDATION
    )
    
    return {
        "score": 85,
        "issues": [
            "Missing keywords from job description",
            "Resume format may not be parsed correctly"
        ],
        "recommendations": [
            "Add more industry-specific keywords",
            "Use a simpler format for better ATS compatibility"
        ]
    }