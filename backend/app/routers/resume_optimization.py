from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.jwt import get_current_active_user
from ..models import User
from ..services.multi_ai_service import MultiAIService
from ..services.document_generator import DocumentGeneratorService
from ..middleware.rate_limiter import rate_limit
import json
import os

router = APIRouter(
    prefix="/api/v1",
    tags=["resume-optimization"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate-resume")
@rate_limit(rate_limit=3, burst_limit=1)  # 3 requests per minute
async def generate_or_optimize_resume(
    job_description: str = Form(...),
    resume_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new resume OR optimize an existing resume based on job description.
    
    Two modes:
    1. Generate New Resume: Only provide job_description (no file)
    2. Optimize Existing Resume: Provide both job_description and resume_file
    """
    try:
        ai_service = MultiAIService()
        
        if resume_file:
            # Mode 2: Optimize existing resume
            print("🔧 Optimizing existing resume...")
            
            # Read and parse the uploaded resume file
            file_content = await resume_file.read()
            file_extension = resume_file.filename.split('.')[-1].lower()
            
            # For now, we'll use the filename as content indicator
            # In a full implementation, you'd parse the actual file content
            resume_text = f"Uploaded resume: {resume_file.filename}"
            
            # Create a user profile from the uploaded resume (simplified)
            user_profile = {
                "name": "User from Resume",
                "email": current_user.email,
                "skills": ["Python", "JavaScript", "React"],  # Would be extracted from resume
                "work_history": [{
                    "company": "Previous Company",
                    "position": "Software Engineer",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "description": "Worked on various projects"
                }],
                "education": [{
                    "degree": "Bachelor's",
                    "major": "Computer Science",
                    "university": "University",
                    "year": "2019"
                }]
            }
            
            # Generate optimized resume
            resume_sections = ai_service.generate_resume_content(
                user_profile=user_profile,
                job_description=job_description
            )
            
        else:
            # Mode 1: Generate new resume
            print("🆕 Generating new resume...")
            
            # Create a generic user profile for new resume generation
            user_profile = {
                "name": "AI Generated User",
                "email": current_user.email,
                "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                "work_history": [{
                    "company": "Tech Solutions Inc.",
                    "position": "Software Developer",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "description": "Developed and maintained web applications using modern technologies"
                }],
                "education": [{
                    "degree": "Bachelor of Science",
                    "major": "Computer Science",
                    "university": "State University",
                    "year": "2019"
                }]
            }
            
            # Generate new resume
            resume_sections = ai_service.generate_resume_content(
                user_profile=user_profile,
                job_description=job_description
            )
        
        # Prepare resume data for document generation
        resume_data = {
            "professional_summary": resume_sections.get("professional_summary", ""),
            "technical_skills": resume_sections.get("technical_skills", ""),
            "work_experience": resume_sections.get("professional_experience", ""),
            "education": resume_sections.get("education", ""),
            "additional_skills": resume_sections.get("additional_skills", ""),
            "mode": "optimize" if resume_file else "generate"
        }
        
        # Generate downloadable documents
        doc_generator = DocumentGeneratorService()
        
        try:
            # Generate DOCX and PDF files
            docx_path = doc_generator.generate_docx(resume_data)
            pdf_path = doc_generator.generate_pdf(resume_data)
            
            # Extract just the filename for the URLs
            docx_filename = os.path.basename(docx_path)
            pdf_filename = os.path.basename(pdf_path)
            
            # Add download URLs to response
            resume_data["docx_url"] = f"/api/v1/download/docx/{docx_filename}"
            resume_data["pdf_url"] = f"/api/v1/download/pdf/{pdf_filename}"
            
        except Exception as e:
            print(f"Warning: Could not generate download files: {str(e)}")
            # Continue without download URLs if document generation fails
            resume_data["docx_url"] = None
            resume_data["pdf_url"] = None
        
        return resume_data
        
    except Exception as e:
        print(f"Error in resume generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
        )


@router.get("/download/docx/{filename}")
async def download_docx(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download a generated DOCX resume file"""
    try:
        doc_generator = DocumentGeneratorService()
        file_path = doc_generator.temp_dir / filename
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=f"resume_{current_user.id}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading DOCX file: {str(e)}"
        )


@router.get("/download/pdf/{filename}")
async def download_pdf(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download a generated PDF resume file"""
    try:
        doc_generator = DocumentGeneratorService()
        file_path = doc_generator.temp_dir / filename
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=f"resume_{current_user.id}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading PDF file: {str(e)}"
        )