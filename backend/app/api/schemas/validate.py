from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ResumeValidationRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000, description="Resume text to validate")
    job_description: Optional[str] = Field(None, min_length=50, max_length=10000, description="Optional job description to validate against")

class ValidationResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    passed: bool
    rule_results: Dict[str, bool]
    suggestions: List[str]