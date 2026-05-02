from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ...services.job_analyzer import JobAnalyzer
from ...auth.models import User
from ...auth.jwt import get_current_active_user
from ..dependencies import rate_limit_dependency
from ..schemas.job import JobAnalysisRequest, JobAnalysisResponse

router = APIRouter(prefix="/api/v1", tags=["jobs"])
job_analyzer = JobAnalyzer()

@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job_description(
    job_request: JobAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Analyze a job description and extract key information
    """
    try:
        result = job_analyzer.analyze_job_description(job_request.job_description)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing job description: {str(e)}"
        )