"""
Schemas for document-related API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    content_type: Optional[str] = None
    
class DocumentCreate(DocumentBase):
    resume_id: int
    
class DocumentResponse(DocumentBase):
    id: int
    resume_id: int
    file_path: str
    file_size: Optional[int] = None
    storage_type: str
    s3_url: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True