from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from ...services.resume_validator import ResumeValidator
from ...auth.models import User
from ...auth.jwt import get_current_active_user
from ..dependencies import rate_limit_dependency
from ..schemas.validate import ResumeValidationRequest, ValidationResponse

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
        raise HTTPException(status_code=500, detail=str(e))
        
        # Check for errors
        if "error" in validation_result:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # Extract rule results
        rule_results = {k: v for k, v in validation_result.items() 
                       if k not in ["overall_score", "passed", "error"]}
        
        # Return formatted response
        return {
            "overall_score": validation_result["overall_score"],
            "passed": validation_result["passed"],
            "rule_results": rule_results
        }
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error validating resume: {str(e)}")