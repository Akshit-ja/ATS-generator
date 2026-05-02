from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class JobAnalysisRequest(BaseModel):
    job_description: str = Field(..., min_length=50, max_length=10000, description="Job description text")

class JobAnalysisResponse(BaseModel):
    skills: List[str] = Field(..., description="Technical skills required for the job")
    tools: List[str] = Field(..., description="Tools and software mentioned in the job")
    methodologies: List[str] = Field(..., description="Methodologies and processes mentioned")
    soft_skills: List[str] = Field(..., description="Soft skills required for the job")
    experience_level: str = Field(..., description="Estimated experience level required")
    
class JobDescriptionBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    description: str = Field(..., min_length=50, max_length=10000)
    
class JobDescriptionCreate(JobDescriptionBase):
    pass
    
class JobDescriptionResponse(JobDescriptionBase):
    id: int
    user_id: int
    skills: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    methodologies: Optional[List[str]] = None
    
    class Config:
        orm_mode = True