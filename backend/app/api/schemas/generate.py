from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ResumeGenerationRequest(BaseModel):
    resume_data: Dict[str, Any] = Field(
        ..., 
        description="Structured resume data including experience, education, and skills"
    )
    job_description: str = Field(
        ..., 
        min_length=50, 
        max_length=10000, 
        description="Job description text to tailor the resume for"
    )
    
class GeneratedResumeResponse(BaseModel):
    id: int
    user_id: int
    content: str
    format: str
    
    class Config:
        orm_mode = True
        
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None