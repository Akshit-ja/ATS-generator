import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app
from app.auth.models import User
from app.auth import jwt as auth_jwt
from app.api import dependencies as api_dependencies
from app.services.resume_service import ResumeService
from app.services.resume_matcher import ResumeMatcher
from app.services.ats_validator import ATSValidator

# Test client
@pytest.fixture
def client(mock_auth, monkeypatch):
    monkeypatch.setattr(api_dependencies, "redis_client", None)
    with TestClient(app) as test_client:
        yield test_client

# Mock authentication
@pytest.fixture
def mock_auth(monkeypatch):
    test_user = User(
        id=1,
        email="test@example.com",
        username="test-user",
        hashed_password="hashed-password",
        is_active=True,
    )

    def get_test_user() -> User:
        return test_user

    monkeypatch.setitem(app.dependency_overrides, auth_jwt.get_current_active_user, get_test_user)
    monkeypatch.setitem(app.dependency_overrides, auth_jwt.get_optional_current_user, get_test_user)
    return test_user

# Mock ResumeService
@pytest.fixture
def mock_resume_service():
    with patch("app.routers.resume.ResumeService") as mock:
        instance = mock.return_value
        
        # Mock generate_resume_content
        instance.generate_resume_content.return_value = {
            "content": "Generated resume content",
            "cost": 0.05
        }
        
        # Mock generate_cover_letter
        instance.generate_cover_letter.return_value = {
            "content": "Generated cover letter content",
            "cost": 0.03
        }
        
        yield instance

# Mock ResumeMatcher
@pytest.fixture
def mock_resume_matcher():
    with patch("app.routers.resume.ResumeMatcher") as mock:
        instance = mock.return_value
        
        # Mock match_resume_to_job
        instance.match_resume_to_job.return_value = {
            "overall_match_score": 85,
            "keyword_match_score": 80,
            "semantic_similarity_score": 90,
            "experience_alignment_score": 85,
            "matched_keywords": ["python", "fastapi", "testing"]
        }
        
        yield instance

# Mock ATSValidator
@pytest.fixture
def mock_ats_validator():
    with patch("app.routers.validate.ATSValidator") as mock:
        instance = mock.return_value
        
        # Mock validate_resume
        instance.validate_resume.return_value = {
            "overall_score": 90,
            "recognized_headers": True,
            "proper_date_formats": True,
            "content_score": 90,
            "suggestions": ["Consider adding more keywords"]
        }
        
        yield instance

# Test data
@pytest.fixture
def resume_data():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "location": "New York, NY",
        "summary": "Experienced software engineer",
        "skills": ["Python", "FastAPI", "Testing"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Co",
                "location": "New York, NY",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": "Developed web applications"
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "University",
                "location": "Boston, MA",
                "graduation_date": "2019-05"
            }
        ],
        "job_description": "Looking for a Python developer with FastAPI experience",
        "template": "modern"
    }

# Test resume generation endpoint
def test_generate_resume(client, mock_auth, mock_resume_service, resume_data):
    response = client.post("/api/v1/resumes/generate", json=resume_data)
    
    assert response.status_code == 200
    assert "content" in response.json()
    assert "cost" in response.json()
    
    # Verify ResumeService was called with correct parameters
    mock_resume_service.generate_resume_content.assert_called_once()
    call_args = mock_resume_service.generate_resume_content.call_args[0]
    assert call_args[0] == resume_data

# Test cover letter generation endpoint
def test_generate_cover_letter(client, mock_auth, mock_resume_service, resume_data):
    cover_letter_data = {
        "resume_data": resume_data,
        "job_description": resume_data["job_description"],
        "company_name": "Tech Co"
    }
    
    response = client.post("/api/v1/resumes/cover-letter", json=cover_letter_data)
    
    assert response.status_code == 200
    assert "content" in response.json()
    assert "cost" in response.json()
    
    # Verify ResumeService was called with correct parameters
    mock_resume_service.generate_cover_letter.assert_called_once()

# Test resume matching endpoint
def test_match_resume(client, mock_auth, mock_resume_matcher):
    match_data = {
        "resume_text": "Python developer with FastAPI experience",
        "job_description": "Looking for a Python developer with FastAPI experience"
    }
    
    response = client.post("/api/v1/resumes/match-score", json=match_data)
    
    assert response.status_code == 200
    assert "overall_match_score" in response.json()
    assert "keyword_match_score" in response.json()
    assert "semantic_similarity_score" in response.json()
    assert "experience_alignment_score" in response.json()
    
    # Verify ResumeMatcher was called with correct parameters
    mock_resume_matcher.match_resume_to_job.assert_called_once_with(
        match_data["resume_text"], match_data["job_description"]
    )

# Test ATS validation endpoint
def test_validate_resume(client, mock_auth, mock_ats_validator):
    validation_data = {
        "resume_text": "Python developer with FastAPI experience",
        "job_description": "Looking for a Python developer with FastAPI experience"
    }
    
    response = client.post("/api/v1/validate/resume", json=validation_data)
    
    assert response.status_code == 200
    assert "overall_score" in response.json()
    assert "recognized_headers" in response.json()
    assert "proper_date_formats" in response.json()
    
    # Verify ATSValidator was called with correct parameters
    mock_ats_validator.validate_resume.assert_called_once_with(
        validation_data["resume_text"], validation_data["job_description"]
    )

# Test error handling
def test_error_handling(client, mock_auth, mock_resume_service):
    # Set up mock to raise an exception
    mock_resume_service.generate_resume_content.side_effect = Exception("Test error")
    
    response = client.post("/api/v1/resumes/generate", json={})
    
    # Should return a 500 error
    assert response.status_code == 500
    assert "detail" in response.json()
