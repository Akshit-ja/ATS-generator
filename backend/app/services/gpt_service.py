"""Compatibility wrapper for GPT-style services used in tests."""
from typing import Any, Dict, List, Optional

from .multi_ai_service import MultiAIService


class GPTService:
    def __init__(self, ai_service: Optional[MultiAIService] = None):
        self.ai_service = ai_service or MultiAIService()

    def generate_resume_content(self, user_profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        return self.ai_service.generate_resume_content(user_profile, job_description)

    def generate_interview_questions(self, job_description: str, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        return self.ai_service.generate_interview_questions(job_description, user_profile)

    def enhance_resume_section(self, section_content: str, section_type: str, job_description: str) -> str:
        return self.ai_service.enhance_resume_section(section_content, section_type, job_description)

    def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        return self.ai_service.analyze_job_match(resume_content, job_description)
