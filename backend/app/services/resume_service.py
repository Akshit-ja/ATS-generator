from typing import Dict, List, Optional, Any
import inspect
from sqlalchemy.orm import Session
from ..db.models import EndpointType
from .token_tracker import TokenTracker
from .multi_ai_service import MultiAIService
from ..core.config import settings

class ResumeService:
    """Service for handling resume operations"""
    
    def __init__(self, db: Session = None, gpt_service: Optional[object] = None):
        self.db = db
        self.token_tracker = TokenTracker(db) if db else None
        self.ai_service = gpt_service or MultiAIService()
    
    def create_resume(self, resume_data: Dict) -> Dict:
        """
        Create a new resume
        
        In a real implementation, this would save to a database
        """
        # Generate a unique ID (simplified for demo)
        resume_id = "resume-" + resume_data["name"].lower().replace(" ", "-")
        
        # Return the resume with ID
        return {**resume_data, "id": resume_id}
    
    def get_resume(self, resume_id: str) -> Optional[Dict]:
        """
        Get a resume by ID
        
        In a real implementation, this would fetch from a database
        """
        # Mock implementation - would be replaced with database lookup
        if resume_id.startswith("resume-"):
            return {
                "id": resume_id,
                "name": "Sample User",
                "email": "user@example.com",
                "skills": ["Python", "FastAPI", "React"]
            }
        return None
    
    def generate_ai_resume(self, user_data: Dict, job_description: str, user_id: int = None, job_id: int = None) -> Dict:
        """
        Generate an AI-enhanced resume based on user data and job description
        
        This is a placeholder for the actual AI implementation
        """
        # In a real implementation, this would call an OpenAI API
        enhanced_skills = user_data.get("skills", []) + ["Communication", "Problem Solving"]
        
        # Mock OpenAI response for demonstration
        mock_openai_response = {
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 250,
                "completion_tokens": 150,
                "total_tokens": 400
            }
        }
        
        # Track token usage if db is available
        if self.token_tracker and user_id:
            self.token_tracker.track_usage_from_response(
                response=mock_openai_response,
                user_id=user_id,
                endpoint_type=EndpointType.RESUME_GENERATION,
                job_id=job_id,
                resume_id=None  # Would be set after resume creation
            )
        
        return {
            **user_data,
            "skills": enhanced_skills,
            "summary": f"Experienced professional with skills matching {job_description}",
            "ai_enhanced": True
        }

    async def generate_resume_content(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        template: str = "modern"
    ) -> Dict[str, Any]:
        """
        Generate resume content using the configured AI service.
        """
        ai_result = await self._maybe_await(
            self.ai_service.generate_resume_content(resume_data, job_description)
        )
        return self._normalize_ai_result(ai_result)

    async def generate_cover_letter(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a cover letter using the configured AI service.
        """
        if hasattr(self.ai_service, "generate_cover_letter"):
            ai_result = await self._maybe_await(
                self.ai_service.generate_cover_letter(resume_data, job_description, style)
            )
            return self._normalize_ai_result(ai_result)

        fallback_content = (
            f"Cover letter for {resume_data.get('name', 'candidate')} "
            f"tailored to: {job_description}"
        )
        return {
            "content": fallback_content,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "cost": 0.0
        }

    def _calculate_cost(self, token_usage: Dict[str, int]) -> float:
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        return (
            (prompt_tokens * settings.GPT_PROMPT_PRICE_PER_1K / 1000)
            + (completion_tokens * settings.GPT_COMPLETION_PRICE_PER_1K / 1000)
        )

    def _normalize_ai_result(self, ai_result: Any) -> Dict[str, Any]:
        if isinstance(ai_result, dict):
            token_usage = ai_result.get("token_usage", {})
            content = ai_result.get("content")
            if content is None:
                content_parts = []
                for key, value in ai_result.items():
                    if key in {"token_usage", "cost"}:
                        continue
                    if isinstance(value, (str, int, float)):
                        content_parts.append(str(value))
                content = "\n".join(content_parts)
            normalized = dict(ai_result)
            normalized.setdefault("content", content)
        else:
            token_usage = {}
            normalized = {"content": str(ai_result)}

        cost = self._calculate_cost(token_usage) if token_usage else 0.0
        normalized.setdefault("token_usage", token_usage)
        normalized["cost"] = cost
        return normalized

    async def _maybe_await(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return await value
        return value
