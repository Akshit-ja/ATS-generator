import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import numpy as np
from app.services.resume_matcher import ResumeMatcher

class TestResumeMatcher(unittest.TestCase):
    
    @patch('app.services.resume_matcher.SentenceTransformer')
    @patch('app.services.resume_matcher.redis.Redis')
    @patch('app.services.resume_matcher.JobAnalyzer')
    def setUp(self, mock_job_analyzer, mock_redis, mock_sentence_transformer):
        # Mock the SentenceTransformer model
        self.mock_model = mock_sentence_transformer.return_value
        
        # Mock Redis client
        self.mock_redis = mock_redis.return_value
        self.mock_redis.ping.return_value = True
        
        # Mock JobAnalyzer
        self.mock_job_analyzer = mock_job_analyzer.return_value
        
        # Create ResumeMatcher instance
        self.resume_matcher = ResumeMatcher()
        
        # Sample data
        self.sample_resume = """
        John Smith
        john.smith@example.com
        
        SKILLS
        Python, FastAPI, React, TypeScript, Docker, AWS
        
        EXPERIENCE
        Senior Software Engineer, Tech Corp (2020-Present)
        - Developed web applications using modern technologies
        - Led team of 5 developers
        
        Software Developer, Dev Inc (2017-2020)
        - Implemented RESTful APIs
        - Worked on frontend using React
        
        EDUCATION
        Bachelor of Science in Computer Science, University of Technology (2017)
        """
        
        self.sample_job_description = """
        Senior Software Engineer
        
        Requirements:
        - 5+ years of experience in software development
        - Proficient in Python and JavaScript
        - Experience with React and TypeScript
        - Knowledge of Docker and containerization
        - AWS experience preferred
        - Strong communication skills
        
        Responsibilities:
        - Develop and maintain web applications
        - Lead a team of developers
        - Collaborate with product managers
        """
        
        self.sample_job_analysis = {
            "skills": ["Python", "JavaScript", "React", "TypeScript"],
            "tools": ["Docker", "AWS"],
            "methodologies": ["web development", "team leadership"],
            "soft_skills": ["communication", "collaboration"],
            "experience_level": "senior"
        }

    def test_generate_hash(self):
        """Test hash generation for cache keys"""
        text = "sample text"
        hash_value = self.resume_matcher._generate_hash(text)
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 32)  # MD5 hash length
        
        # Same input should produce same hash
        hash_value2 = self.resume_matcher._generate_hash(text)
        self.assertEqual(hash_value, hash_value2)
        
        # Different input should produce different hash
        hash_value3 = self.resume_matcher._generate_hash("different text")
        self.assertNotEqual(hash_value, hash_value3)

    def test_calculate_keyword_coverage(self):
        """Test keyword coverage calculation"""
        # Test with matching keywords
        coverage, missing = self.resume_matcher._calculate_keyword_coverage(
            self.sample_resume, self.sample_job_analysis
        )
        
        self.assertIsInstance(coverage, float)
        self.assertGreaterEqual(coverage, 0)
        self.assertLessEqual(coverage, 100)
        self.assertIsInstance(missing, list)
        
        # Test with no matching keywords
        empty_resume = "No relevant skills mentioned here"
        coverage, missing = self.resume_matcher._calculate_keyword_coverage(
            empty_resume, self.sample_job_analysis
        )
        self.assertEqual(coverage, 0.0)
        self.assertEqual(len(missing), len(self.sample_job_analysis["skills"] + 
                                          self.sample_job_analysis["tools"] + 
                                          self.sample_job_analysis["methodologies"]))
        
        # Test with empty job analysis
        empty_job_analysis = {"skills": [], "tools": [], "methodologies": []}
        coverage, missing = self.resume_matcher._calculate_keyword_coverage(
            self.sample_resume, empty_job_analysis
        )
        self.assertEqual(coverage, 0.0)
        self.assertEqual(missing, [])

    @patch('backend.app.services.resume_matcher.np')
    def test_calculate_semantic_similarity(self, mock_np):
        """Test semantic similarity calculation"""
        # Mock numpy operations
        mock_np.dot.return_value = 0.85
        mock_np.linalg.norm.return_value = 1.0
        
        # Set up model encode mock
        self.mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        similarity = self.resume_matcher._calculate_semantic_similarity(
            self.sample_resume, self.sample_job_description
        )
        
        self.assertIsInstance(similarity, float)
        self.assertEqual(similarity, 85.0)  # 0.85 * 100
        
        # Test exception handling
        self.mock_model.encode.side_effect = Exception("Model error")
        similarity = self.resume_matcher._calculate_semantic_similarity(
            self.sample_resume, self.sample_job_description
        )
        self.assertEqual(similarity, 0.0)

    def test_calculate_experience_alignment(self):
        """Test experience alignment calculation"""
        # Test exact match
        alignment = self.resume_matcher._calculate_experience_alignment(
            "Senior developer with 7+ years of experience", "senior"
        )
        self.assertEqual(alignment, 100.0)
        
        # Test senior resume for mid-level job
        alignment = self.resume_matcher._calculate_experience_alignment(
            "Senior developer with 7+ years of experience", "mid"
        )
        self.assertEqual(alignment, 80.0)
        
        # Test entry-level resume for senior job
        alignment = self.resume_matcher._calculate_experience_alignment(
            "Junior developer, recent graduate", "senior"
        )
        self.assertEqual(alignment, 20.0)
        
        # Test unspecified job level
        alignment = self.resume_matcher._calculate_experience_alignment(
            "Developer with experience", "not specified"
        )
        self.assertEqual(alignment, 50.0)

    def test_calculate_overall_score(self):
        """Test overall score calculation"""
        score = self.resume_matcher._calculate_overall_score(80.0, 70.0, 90.0)
        # Expected: (80 * 0.5) + (70 * 0.3) + (90 * 0.2) = 79
        self.assertEqual(score, 79)
        
        # Test with zeros
        score = self.resume_matcher._calculate_overall_score(0.0, 0.0, 0.0)
        self.assertEqual(score, 0)
        
        # Test with 100s
        score = self.resume_matcher._calculate_overall_score(100.0, 100.0, 100.0)
        self.assertEqual(score, 100)

    @patch('backend.app.services.resume_matcher.ResumeMatcher._get_from_cache')
    @patch('backend.app.services.resume_matcher.ResumeMatcher._save_to_cache')
    def test_match_resume_to_job_with_cache_hit(self, mock_save_cache, mock_get_cache):
        """Test match_resume_to_job with cache hit"""
        # Mock cache hit
        mock_get_cache.return_value = self.sample_job_analysis
        
        # Set up mocks for score calculations
        self.resume_matcher._calculate_keyword_coverage = MagicMock(return_value=(75.0, ["JavaScript"]))
        self.resume_matcher._calculate_semantic_similarity = MagicMock(return_value=80.0)
        self.resume_matcher._calculate_experience_alignment = MagicMock(return_value=90.0)
        self.resume_matcher._calculate_overall_score = MagicMock(return_value=80)
        
        # Call the method
        result = self.resume_matcher.match_resume_to_job(
            self.sample_resume, self.sample_job_description
        )
        
        # Verify cache was checked but not saved
        mock_get_cache.assert_called_once()
        mock_save_cache.assert_not_called()
        
        # Verify result structure
        self.assertEqual(result["overall_match_score"], 80)
        self.assertEqual(result["breakdown"]["keyword_coverage"], 75.0)
        self.assertEqual(result["breakdown"]["semantic_similarity"], 80.0)
        self.assertEqual(result["breakdown"]["experience_alignment"], 90.0)
        self.assertEqual(result["missing_critical_keywords"], ["JavaScript"])

    @patch('backend.app.services.resume_matcher.ResumeMatcher._get_from_cache')
    @patch('backend.app.services.resume_matcher.ResumeMatcher._save_to_cache')
    def test_match_resume_to_job_with_cache_miss(self, mock_save_cache, mock_get_cache):
        """Test match_resume_to_job with cache miss"""
        # Mock cache miss
        mock_get_cache.return_value = None
        
        # Mock job analyzer
        self.resume_matcher.job_analyzer.analyze_job_description.return_value = self.sample_job_analysis
        
        # Set up mocks for score calculations
        self.resume_matcher._calculate_keyword_coverage = MagicMock(return_value=(75.0, ["JavaScript"]))
        self.resume_matcher._calculate_semantic_similarity = MagicMock(return_value=80.0)
        self.resume_matcher._calculate_experience_alignment = MagicMock(return_value=90.0)
        self.resume_matcher._calculate_overall_score = MagicMock(return_value=80)
        
        # Call the method
        result = self.resume_matcher.match_resume_to_job(
            self.sample_resume, self.sample_job_description
        )
        
        # Verify cache was checked and saved
        mock_get_cache.assert_called_once()
        mock_save_cache.assert_called_once()
        
        # Verify job analyzer was called
        self.resume_matcher.job_analyzer.analyze_job_description.assert_called_once_with(
            self.sample_job_description
        )
        
        # Verify result structure
        self.assertEqual(result["overall_match_score"], 80)

if __name__ == '__main__':
    unittest.main()
