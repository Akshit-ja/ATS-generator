from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import List, Optional, Dict, Any
import re

class ResumeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the person")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-\(\)]{8,20}$", description="Phone number")
    summary: Optional[str] = Field(None, min_length=10, max_length=2000, description="Professional summary")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    
    @validator('skills')
    def validate_skills(cls, v):
        if len(v) > 50:
            raise ValueError('Maximum 50 skills allowed')
        return v

class ExperienceItem(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    company: str = Field(..., min_length=2, max_length=100)
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}$|^\d{4}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$|^\d{4}$|^Present$")
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if v and v != "Present" and 'start_date' in values:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class EducationItem(BaseModel):
    degree: str = Field(..., min_length=2, max_length=100)
    institution: str = Field(..., min_length=2, max_length=100)
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}$|^\d{4}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$|^\d{4}$|^Present$")
    description: Optional[str] = Field(None, max_length=1000)

class ResumeCreate(ResumeBase):
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    
    @validator('experience')
    def validate_experience(cls, v):
        if len(v) > 15:
            raise ValueError('Maximum 15 experience items allowed')
        return v
    
    @validator('education')
    def validate_education(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 education items allowed')
        return v

class ResumeResponse(ResumeCreate):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True

class ParsedResumeResponse(BaseModel):
    text: str = Field(..., min_length=10)
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    sections: List[str] = Field(default_factory=list)

class JobDescriptionBase(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    description: str = Field(..., min_length=50, max_length=10000, description="Job description text")

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

class JobAnalysisResponse(BaseModel):
    skills: List[str]
    tools: List[str]
    methodologies: List[str]
    soft_skills: List[str]
    experience_level: str

class MatchScoreRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000)
    job_description: str = Field(..., min_length=50, max_length=10000)

class MatchScoreResponse(BaseModel):
    overall_match_score: int = Field(..., ge=0, le=100)
    breakdown: Dict[str, float]
    missing_critical_keywords: List[str]

class ResumeGenerationRequest(BaseModel):
    resume_data: Dict[str, Any] = Field(..., description="Structured resume data")
    job_description: str = Field(..., min_length=50, max_length=10000, description="Job description text")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ValidationResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    passed: bool
    rule_results: Dict[str, bool]