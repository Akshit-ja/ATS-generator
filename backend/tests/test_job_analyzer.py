import pytest
from unittest.mock import patch, MagicMock
from app.services.job_analyzer import JobAnalyzer
from collections import Counter

class TestJobAnalyzer:
    @pytest.fixture
    def job_analyzer(self):
        return JobAnalyzer()
    
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
        - Strong understanding of RESTful APIs
        - Experience with SQL and NoSQL databases
        
        Nice to have:
        - Experience with React or other frontend frameworks
        - Knowledge of CI/CD pipelines
        - Experience with microservices architecture
        """
    
    def test_clean_text(self, job_analyzer, sample_job_description):
        cleaned_text = job_analyzer._clean_text(sample_job_description)
        assert cleaned_text.lower() == sample_job_description.lower()
        assert "senior software engineer" in cleaned_text.lower()
        assert "python" in cleaned_text.lower()
    
    def test_extract_keywords(self, job_analyzer):
        text = "Python developer with FastAPI and Docker experience needed for AWS projects"
        keywords = job_analyzer._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert any(keyword.lower() == "python" for keyword in keywords)
        assert any(keyword.lower() == "fastapi" for keyword in keywords)
        assert any(keyword.lower() == "docker" for keyword in keywords)
        assert any(keyword.lower() == "aws" for keyword in keywords)
    
    def test_categorize_keywords(self, job_analyzer):
        keywords = ["Python", "JavaScript", "Docker", "AWS", "communication", "teamwork", "agile"]
        
        with patch.object(job_analyzer, 'skill_keywords', ["python", "javascript"]):
            with patch.object(job_analyzer, 'tool_keywords', ["docker", "aws"]):
                with patch.object(job_analyzer, 'methodology_keywords', ["agile"]):
                    with patch.object(job_analyzer, 'soft_skill_keywords', ["communication", "teamwork"]):
                        result = job_analyzer._categorize_keywords(keywords)
        
        assert "skills" in result
        assert "tools" in result
        assert "methodologies" in result
        assert "soft_skills" in result
        
        assert "Python" in result["skills"]
        assert "JavaScript" in result["skills"]
        assert "Docker" in result["tools"]
        assert "AWS" in result["tools"]
        assert "agile" in result["methodologies"]
        assert "communication" in result["soft_skills"]
        assert "teamwork" in result["soft_skills"]
    
    def test_determine_experience_level(self, job_analyzer):
        entry_text = "Entry level position, 0-1 years of experience required"
        mid_text = "Mid-level developer with 3 years of experience"
        senior_text = "Senior position requiring 5+ years of experience"
        
        assert job_analyzer._determine_experience_level(entry_text) == "entry"
        assert job_analyzer._determine_experience_level(mid_text) == "mid"
        assert job_analyzer._determine_experience_level(senior_text) == "senior"
    
    def test_analyze_job_description(self, job_analyzer, sample_job_description):
        with patch.object(job_analyzer, '_clean_text', return_value=sample_job_description):
            with patch.object(job_analyzer, '_extract_keywords', return_value=["Python", "FastAPI", "Docker", "AWS"]):
                with patch.object(job_analyzer, '_categorize_keywords', return_value={
                    "skills": ["Python", "FastAPI"],
                    "tools": ["Docker", "AWS"],
                    "methodologies": ["RESTful API"],
                    "soft_skills": ["communication"]
                }):
                    with patch.object(job_analyzer, '_determine_experience_level', return_value="senior"):
                        result = job_analyzer.analyze_job_description(sample_job_description)
        
        assert "skills" in result
        assert "tools" in result
        assert "methodologies" in result
        assert "soft_skills" in result
        assert "experience_level" in result
        assert result["experience_level"] == "senior"
    
    def test_analyze_job_description_exception(self, job_analyzer, sample_job_description):
        with patch.object(job_analyzer, '_clean_text', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as excinfo:
                job_analyzer.analyze_job_description(sample_job_description)
            assert "Test error" in str(excinfo.value)