from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Dict
from ...services.resume_validator import ResumeValidator
from ...auth.models import User
from ...auth.jwt import get_current_active_user
from ..dependencies import rate_limit_dependency
from ..schemas.validate import ResumeValidationRequest, ValidationResponse
from ...routers import validate as legacy_validate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["validate"])
validator = ResumeValidator()
    
@router.post("/validate", response_model=ValidationResponse)
async def validate_resume(
    validation_request: ResumeValidationRequest,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Validate a resume text for ATS compliance.
    
    This endpoint checks a resume against ATS compliance rules and returns
    a pass/fail result for each rule along with an overall compliance score.
    """
    try:
        # Validate the resume
        validation_result = validator.validate(
            validation_request.resume_text, 
            validation_request.job_description
        )
        
        return validation_result
    except Exception as e:
        logger.exception("Resume validation failed")
        raise HTTPException(status_code=500, detail="Error validating resume")

@router.post("/validate/resume")
async def validate_resume_text(
    validation_data: Dict,
    current_user: User = Depends(legacy_validate.get_current_active_user),
    _: None = Depends(rate_limit_dependency())
):
    """
    Validate resume text for ATS compliance (integration-test endpoint).
    """
    validator = legacy_validate.ATSValidator()
    try:
        resume_text = validation_data.get("resume_text", "")
        job_description = validation_data.get("job_description")
        result = validator.validate_resume(resume_text, job_description)
        if not isinstance(result, dict):
            return result
        if result.get("error"):
            logger.error("Resume validation error: %s", result.get("error"))
            raise HTTPException(status_code=500, detail="Error validating resume")
        return {
            "overall_score": result.get("overall_score", 0),
            "recognized_headers": result.get("recognized_headers", False),
            "proper_date_formats": result.get("proper_date_formats", False),
            "content_score": result.get("content_score", result.get("overall_score", 0)),
            "suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        logger.exception("Resume text validation failed")
        raise HTTPException(status_code=500, detail="Error validating resume")
