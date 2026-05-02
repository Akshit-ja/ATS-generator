import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from app.services.resume_service import ResumeService
from app.services.multi_ai_service import MultiAIService
from app.core.config import settings

class TestResumeGeneration:
    @pytest.fixture
    def resume_service(self):
        # ResumeService uses MultiAIService as `ai_service`
        with patch('app.services.resume_service.MultiAIService') as mock_ai:
            service = ResumeService()
            service.ai_service = mock_ai.return_value
            yield service

    @pytest.fixture
    def sample_user_data(self):
        return {
            "id": "user123",
            "email": "test@example.com"
        }

    @pytest.fixture
    def sample_resume_data(self):
        return {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "123-456-7890",
            "location": "New York, NY",
            "summary": "Experienced software engineer with 5+ years in web development",
            "skills": ["Python", "JavaScript", "React", "FastAPI"],
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Company",
                    "location": "New York, NY",
                    "start_date": "2020-01",
                    "end_date": "Present",
                    "description": "Led development of web applications"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Technology",
                    "location": "Boston, MA",
                    "graduation_date": "2017-05"
                }
            ]
        }

    @pytest.fixture
    def sample_job_description(self):
        return """
        Senior Software Engineer - Python

        We are looking for a Senior Software Engineer with strong Python skills to join our team.

        Requirements:
        - 5+ years of experience with Python
        - Experience with web frameworks like FastAPI or Flask
        - Knowledge of Docker and containerization
        - Experience with AWS cloud services
        """

    @pytest.mark.asyncio
    async def test_generate_resume_content(self, resume_service, sample_resume_data, sample_job_description):
        # MultiAIService in this repo exposes generate_resume_content(user_profile, job_description)
        mock_ai_response = {
            "content": "This is a generated resume content",
            "token_usage": {
                "prompt_tokens": 500,
                "completion_tokens": 300,
                "total_tokens": 800
            }
        }
        resume_service.ai_service.generate_resume_content = AsyncMock(return_value=mock_ai_response)

        result = await resume_service.generate_resume_content(
            sample_resume_data,
            sample_job_description,
            "modern"
        )

        assert result["content"] == "This is a generated resume content"
        assert "token_usage" in result
        assert result["token_usage"]["total_tokens"] == 800

        resume_service.ai_service.generate_resume_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_cover_letter(self, resume_service, sample_resume_data, sample_job_description):
        mock_ai_response = {
            "content": "This is a generated cover letter",
            "token_usage": {
                "prompt_tokens": 400,
                "completion_tokens": 200,
                "total_tokens": 600
            }
        }
        resume_service.ai_service.generate_cover_letter = AsyncMock(return_value=mock_ai_response)

        result = await resume_service.generate_cover_letter(
            sample_resume_data,
            sample_job_description,
            "professional"
        )

        assert result["content"] == "This is a generated cover letter"
        assert "token_usage" in result
        assert result["token_usage"]["total_tokens"] == 600

        resume_service.ai_service.generate_cover_letter.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_resume_with_error(self, resume_service, sample_resume_data, sample_job_description):
        resume_service.ai_service.generate_resume_content = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(Exception) as excinfo:
            await resume_service.generate_resume_content(
                sample_resume_data,
                sample_job_description,
                "modern"
            )

        assert "API error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_calculate_cost(self, resume_service):
        token_usage = {
            "prompt_tokens": 500,
            "completion_tokens": 300,
            "total_tokens": 800
        }

        with patch.object(settings, 'GPT_PROMPT_PRICE_PER_1K', 0.01):
            with patch.object(settings, 'GPT_COMPLETION_PRICE_PER_1K', 0.02):
                cost = resume_service._calculate_cost(token_usage)

                expected_cost = (500 * 0.01 / 1000) + (300 * 0.02 / 1000)
                assert cost == expected_cost
