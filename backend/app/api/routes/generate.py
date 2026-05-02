from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from celery.result import AsyncResult
from ...tasks import generate_resume_task
from ...services.job_analyzer import JobAnalyzer
from ...auth.models import User
from ...auth.jwt import get_current_active_user
from ..dependencies import rate_limit_dependency
from ..schemas.generate import ResumeGenerationRequest, TaskStatusResponse


router = APIRouter(prefix="/api/v1", tags=["generate"])
job_analyzer = JobAnalyzer()


@router.post("/generate", response_model=TaskStatusResponse)
async def generate_resume(
    request: ResumeGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_dependency("premium"))
):
    """
    Generate a tailored resume and cover letter based on resume data and job description.
    This endpoint triggers an asynchronous task and returns a task ID for status tracking.
    """
    try:
        # Analyze job description
        job_analysis = job_analyzer.analyze_job_description(request.job_description)
        
        # Submit Celery task
        task = generate_resume_task.delay(request.resume_data, job_analysis, current_user.id)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "result": None,
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")


@router.get("/generate/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a resume generation task by its ID.
    """
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                "task_id": task_id,
                "status": "pending",
                "result": None,
                "error": None
            }
        elif task_result.state == 'FAILURE':
            response = {
                "task_id": task_id,
                "status": "failed",
                "result": None,
                "error": str(task_result.info)
            }
        else:
            if task_result.info and isinstance(task_result.info, dict) and "status" in task_result.info:
                # Task is in progress with custom state
                response = {
                    "task_id": task_id,
                    "status": task_result.info.get("status", task_result.state.lower()),
                    "result": None,
                    "error": None
                }
            elif task_result.ready():
                # Task is complete
                response = {
                    "task_id": task_id,
                    "status": "completed",
                    "result": task_result.result,
                    "error": None
                }
            else:
                response = {
                    "task_id": task_id,
                    "status": task_result.state.lower(),
                    "result": None,
                    "error": None
                }
                
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")
