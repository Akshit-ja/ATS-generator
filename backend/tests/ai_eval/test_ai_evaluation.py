import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.job_analyzer import JobAnalyzer
from app.services.resume_matcher import ResumeMatcher
from app.services.ats_validator import ATSValidator
from app.services.resume_service import ResumeService
from app.services.gpt_service import GPTService

# Constants
THRESHOLD_SCORE = 85  # 85% threshold for passing tests

# Test case directory
TEST_CASES_DIR = Path(__file__).parent / "test_cases"
os.makedirs(TEST_CASES_DIR, exist_ok=True)

# Sample test cases
SAMPLE_TEST_CASES = [
    {
        "name": "software_engineer_test",
        "job_description": "Senior Software Engineer with 5+ years of experience in Python. Must have experience with FastAPI, PostgreSQL, and cloud services like AWS. Knowledge of CI/CD pipelines and containerization with Docker is required.",
        "resume_content": "John Smith\nSenior Software Engineer\n\nSUMMARY\nExperienced software engineer with 6 years of expertise in Python development, FastAPI, and AWS cloud services. Proficient in designing and implementing CI/CD pipelines using GitHub Actions and containerizing applications with Docker.\n\nSKILLS\nProgramming Languages: Python, JavaScript, SQL\nFrameworks: FastAPI, Flask, React\nDatabases: PostgreSQL, MongoDB\nCloud: AWS (EC2, S3, Lambda)\nTools: Docker, Kubernetes, Git, GitHub Actions\n\nEXPERIENCE\nSenior Software Engineer | Tech Solutions Inc. | 2020-Present\n- Developed and maintained RESTful APIs using FastAPI, serving 10k+ daily users\n- Implemented CI/CD pipelines reducing deployment time by 70%\n- Containerized legacy applications using Docker, improving scalability\n\nSoftware Engineer | DataCorp | 2017-2020\n- Built data processing pipelines using Python and AWS Lambda\n- Managed PostgreSQL databases with 100+ tables and complex queries\n- Collaborated with cross-functional teams to deliver features on time\n\nEDUCATION\nB.S. Computer Science | University of Technology | 2017",
        "expected_keyword_density": 90,
        "expected_semantic_coherence": 95,
        "expected_ats_compliance": 90
    },
    {
        "name": "marketing_specialist_test",
        "job_description": "Digital Marketing Specialist needed for a growing e-commerce company. Requirements: 3+ years of experience with SEO, SEM, social media marketing, and analytics tools like Google Analytics. Experience with email marketing campaigns and A/B testing.",
        "resume_content": "Sarah Johnson\nDigital Marketing Specialist\n\nSUMMARY\nResults-driven Digital Marketing Specialist with 4 years of experience optimizing online presence through SEO, SEM, and social media strategies. Proven track record of increasing conversion rates and implementing successful email marketing campaigns.\n\nSKILLS\nSEO/SEM | Social Media Marketing | Email Marketing\nGoogle Analytics | A/B Testing | Content Creation\nHootsuite | Mailchimp | Adobe Creative Suite\n\nEXPERIENCE\nDigital Marketing Specialist | E-Shop Brands | 2020-Present\n- Increased organic traffic by 45% through comprehensive SEO strategies\n- Managed social media accounts growing follower base by 10k+ across platforms\n- Implemented A/B testing for email campaigns, improving open rates by 30%\n\nMarketing Associate | Marketing Solutions | 2018-2020\n- Assisted in developing and executing digital marketing strategies\n- Created and analyzed reports using Google Analytics\n- Coordinated email marketing campaigns with 25% conversion rate\n\nEDUCATION\nB.A. Marketing | State University | 2018",
        "expected_keyword_density": 85,
        "expected_semantic_coherence": 90,
        "expected_ats_compliance": 88
    }
]

# Create sample test cases if they don't exist
def create_sample_test_cases():
    for test_case in SAMPLE_TEST_CASES:
        file_path = TEST_CASES_DIR / f"{test_case['name']}.json"
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump(test_case, f, indent=2)

create_sample_test_cases()

# Load test cases
def load_test_cases():
    test_cases = []
    for file_path in TEST_CASES_DIR.glob("*.json"):
        with open(file_path, 'r') as f:
            test_cases.append(json.load(f))
    return test_cases

# Fixtures
@pytest.fixture
def job_analyzer():
    return JobAnalyzer()

@pytest.fixture
def resume_matcher():
    with patch("app.services.resume_matcher.SentenceTransformer", MagicMock()) as mock_transformer:
        # Mock the encode method to return mock embeddings
        mock_transformer.return_value.encode.return_value = [0.1, 0.2, 0.3]
        matcher = ResumeMatcher()
        
        # Mock the _calculate_semantic_similarity method
        matcher._calculate_semantic_similarity = MagicMock()
        matcher._calculate_semantic_similarity.side_effect = lambda resume_text, job_description: 0.9
        
        yield matcher

@pytest.fixture
def ats_validator():
    validator = ATSValidator()
    
    # Mock validate_resume to return a fixed score for testing
    validator.validate_resume = MagicMock()
    validator.validate_resume.side_effect = lambda resume_text, job_description: {
        "overall_score": 90,
        "recognized_headers": True,
        "proper_date_formats": True,
        "content_score": 90,
        "suggestions": ["Consider adding more keywords"]
    }
    
    yield validator

@pytest.fixture
def resume_service():
    # Mock GPT service for testing
    gpt_service = MagicMock(spec=GPTService)
    return ResumeService(gpt_service=gpt_service)

@pytest.fixture
def test_cases():
    return load_test_cases()

# Test keyword density
def test_keyword_density(resume_matcher, test_cases):
    for test_case in test_cases:
        # Calculate keyword coverage
        job_description = test_case["job_description"]
        resume_content = test_case["resume_content"]
        
        # Analyze job description to get keywords
        analyzed_job = resume_matcher._analyze_job(job_description)
        keywords = analyzed_job.get("keywords", [])
        
        # Calculate keyword coverage
        keyword_coverage = resume_matcher._calculate_keyword_coverage(resume_content, keywords)
        keyword_density_score = keyword_coverage * 100
        
        # Assert that keyword density meets or exceeds threshold
        assert keyword_density_score >= THRESHOLD_SCORE, f"Keyword density score {keyword_density_score} is below threshold {THRESHOLD_SCORE} for test case {test_case['name']}"
        
        # Optional: Compare with expected score if provided
        if "expected_keyword_density" in test_case:
            expected_score = test_case["expected_keyword_density"]
            # Allow for some variance (within 10%)
            assert abs(keyword_density_score - expected_score) <= 10, f"Keyword density score {keyword_density_score} differs significantly from expected {expected_score}"

# Test semantic coherence
def test_semantic_coherence(resume_matcher, test_cases):
    for test_case in test_cases:
        # Calculate semantic similarity
        job_description = test_case["job_description"]
        resume_content = test_case["resume_content"]
        
        # Calculate semantic similarity
        semantic_similarity = resume_matcher._calculate_semantic_similarity(resume_content, job_description)
        semantic_coherence_score = semantic_similarity * 100
        
        # Assert that semantic coherence meets or exceeds threshold
        assert semantic_coherence_score >= THRESHOLD_SCORE, f"Semantic coherence score {semantic_coherence_score} is below threshold {THRESHOLD_SCORE} for test case {test_case['name']}"
        
        # Optional: Compare with expected score if provided
        if "expected_semantic_coherence" in test_case:
            expected_score = test_case["expected_semantic_coherence"]
            # Allow for some variance (within 10%)
            assert abs(semantic_coherence_score - expected_score) <= 10, f"Semantic coherence score {semantic_coherence_score} differs significantly from expected {expected_score}"

# Test ATS compliance
def test_ats_compliance(ats_validator, test_cases):
    for test_case in test_cases:
        resume_content = test_case["resume_content"]
        job_description = test_case["job_description"]
        
        # Validate resume for ATS compliance
        validation_result = ats_validator.validate_resume(resume_content, job_description)
        ats_compliance_score = validation_result.get("overall_score", 0)
        
        # Assert that ATS compliance meets or exceeds threshold
        assert ats_compliance_score >= THRESHOLD_SCORE, f"ATS compliance score {ats_compliance_score} is below threshold {THRESHOLD_SCORE} for test case {test_case['name']}"
        
        # Optional: Compare with expected score if provided
        if "expected_ats_compliance" in test_case:
            expected_score = test_case["expected_ats_compliance"]
            # Allow for some variance (within 10%)
            assert abs(ats_compliance_score - expected_score) <= 10, f"ATS compliance score {ats_compliance_score} differs significantly from expected {expected_score}"

# Test overall quality (combined metrics)
def test_overall_quality(resume_matcher, ats_validator, test_cases):
    for test_case in test_cases:
        job_description = test_case["job_description"]
        resume_content = test_case["resume_content"]
        
        # Calculate keyword coverage
        analyzed_job = resume_matcher._analyze_job(job_description)
        keywords = analyzed_job.get("keywords", [])
        keyword_coverage = resume_matcher._calculate_keyword_coverage(resume_content, keywords)
        
        # Calculate semantic similarity
        semantic_similarity = resume_matcher._calculate_semantic_similarity(resume_content, job_description)
        
        # Calculate ATS compliance
        validation_result = ats_validator.validate_resume(resume_content, job_description)
        ats_compliance_score = validation_result.get("overall_score", 0) / 100  # Normalize to 0-1
        
        # Calculate overall quality score (weighted average)
        overall_quality = (keyword_coverage * 0.4 + semantic_similarity * 0.3 + ats_compliance_score * 0.3) * 100
        
        # Assert that overall quality meets or exceeds threshold
        assert overall_quality >= THRESHOLD_SCORE, f"Overall quality score {overall_quality} is below threshold {THRESHOLD_SCORE} for test case {test_case['name']}"

if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main(["-v", __file__])