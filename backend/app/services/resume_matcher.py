import redis
import json
import hashlib
from typing import Dict, List, Tuple, Optional
import logging
from .job_analyzer import JobAnalyzer
from .redis_metrics import instrument_redis_methods
from ..core.telemetry import get_tracer
import os

logger = logging.getLogger(__name__)
tracer = get_tracer("resume_matcher")

@instrument_redis_methods
class ResumeMatcher:
    """Service for matching resumes to job descriptions"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        try:
            # ML model disabled for simplified version
            self.model = None
            
            # Initialize Redis client
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_available = True
            try:
                self.redis.ping()
            except redis.exceptions.ConnectionError:
                logger.warning("Redis connection failed. Caching will be disabled.")
                self.redis_available = False
                
            # Initialize job analyzer
            self.job_analyzer = JobAnalyzer()
            
            # Cache TTL in seconds (1 day)
            self.cache_ttl = 86400
            
        except Exception as e:
            logger.error(f"Error initializing ResumeMatcher: {str(e)}")
            self.redis_available = False
            # Re-raise if it's a critical error like missing model
            if "SentenceTransformer" in str(e):
                raise
    
    def calculate_match_score(self, resume_text: str, job_description: str) -> Dict:
        """Calculate match score - alias for match_resume_to_job"""
        return self.match_resume_to_job(resume_text, job_description)
    
    def match_resume_to_job(self, resume_text: str, job_description: str) -> Dict:
        """Match a resume to a job description and calculate match scores"""
        with tracer.start_as_current_span("match_resume_to_job") as span:
            span.set_attribute("resume.length", len(resume_text))
            span.set_attribute("job_description.length", len(job_description))
            try:
                # Generate cache key for job description
                job_hash = self._generate_hash(job_description)
                cache_key = f"job_analysis:{job_hash}"
                
                # Try to get job analysis from cache
                job_analysis = self._get_from_cache(cache_key)
                
                if not job_analysis:
                    span.set_attribute("cache.hit", False)
                    # Analyze job description
                    job_analysis = self.job_analyzer.analyze_job_description(job_description)
                    
                    # Cache the job analysis
                    self._save_to_cache(cache_key, job_analysis)
                else:
                    span.set_attribute("cache.hit", True)
                
                # Calculate keyword coverage
                keyword_coverage, missing_keywords = self._calculate_keyword_coverage(
                    resume_text, job_analysis
                )
                
                # Calculate semantic similarity
                semantic_similarity = self._calculate_semantic_similarity(
                    resume_text, job_description
                )
                
                # Calculate experience alignment
                experience_alignment = self._calculate_experience_alignment(
                    resume_text, job_analysis["experience_level"]
                )
                
                # Calculate overall match score
                overall_score = self._calculate_overall_score(
                    keyword_coverage, semantic_similarity, experience_alignment
                )
                
                return {
                    "overall_match_score": overall_score,
                    "breakdown": {
                        "keyword_coverage": keyword_coverage,
                        "semantic_similarity": semantic_similarity,
                        "experience_alignment": experience_alignment
                    },
                    "missing_critical_keywords": missing_keywords
                }
            except Exception as e:
                logger.error(f"Error matching resume to job: {str(e)}")
                raise
    
    def _generate_hash(self, text: str) -> str:
        """Generate a hash for the text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from Redis cache"""
        if not self.redis_available:
            return None
        
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    def _save_to_cache(self, key: str, data: Dict) -> bool:
        """Save data to Redis cache"""
        if not self.redis_available:
            return False
        
        try:
            self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Redis save error: {str(e)}")
            return False
    
    def _calculate_keyword_coverage(self, resume_text: str, job_analysis: Dict) -> Tuple[float, List[str]]:
        """Calculate keyword coverage score and identify missing keywords"""
        resume_text_lower = resume_text.lower()
        
        # Combine all job keywords
        all_keywords = []
        for category in ["skills", "tools", "methodologies"]:
            all_keywords.extend(job_analysis.get(category, []))
        
        if not all_keywords:
            return 0.0, []
        
        # Count matched keywords
        matched_keywords = []
        missing_keywords = []
        
        for keyword in all_keywords:
            if keyword.lower() in resume_text_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate coverage score
        coverage_score = len(matched_keywords) / len(all_keywords) * 100 if all_keywords else 0.0
        
        # Return top missing keywords (max 10)
        return coverage_score, missing_keywords[:10]
    
    def _calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate basic similarity score without ML model"""
        try:
            # Simple word overlap calculation as fallback
            resume_words = set(resume_text.lower().split())
            job_words = set(job_description.lower().split())
            
            if not resume_words or not job_words:
                return 0.0
                
            # Calculate Jaccard similarity
            intersection = len(resume_words.intersection(job_words))
            union = len(resume_words.union(job_words))
            
            similarity_score = (intersection / union) * 100 if union > 0 else 0.0
            
            return similarity_score
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {str(e)}")
            return 0.0
    
    def _calculate_experience_alignment(self, resume_text: str, job_experience_level: str) -> float:
        """Calculate experience alignment score"""
        resume_text_lower = resume_text.lower()
        
        # Define experience indicators for each level
        experience_indicators = {
            "entry": ["intern", "internship", "entry level", "junior", "graduate", "0-1 year", "0-2 years"],
            "mid": ["mid level", "intermediate", "2-5 years", "3-5 years", "experienced"],
            "senior": ["senior", "lead", "5+ years", "7+ years", "10+ years", "principal", "architect", "manager"]
        }
        
        # If job doesn't specify experience level
        if job_experience_level == "not specified":
            return 50.0
        
        # Count indicators in resume for each level
        level_counts = {level: 0 for level in experience_indicators.keys()}
        
        for level, indicators in experience_indicators.items():
            for indicator in indicators:
                if indicator in resume_text_lower:
                    level_counts[level] += 1
        
        # Determine resume experience level
        if sum(level_counts.values()) == 0:
            resume_level = "not specified"
        else:
            resume_level = max(level_counts.items(), key=lambda x: x[1])[0]
        
        # Calculate alignment score
        if resume_level == "not specified" or job_experience_level == "not specified":
            return 50.0
        elif resume_level == job_experience_level:
            return 100.0
        elif (resume_level == "senior" and job_experience_level == "mid") or (resume_level == "mid" and job_experience_level == "entry"):
            return 80.0
        elif resume_level == "senior" and job_experience_level == "entry":
            return 60.0
        elif (resume_level == "mid" and job_experience_level == "senior") or (resume_level == "entry" and job_experience_level == "mid"):
            return 40.0
        elif resume_level == "entry" and job_experience_level == "senior":
            return 20.0
        else:
            return 50.0
    
    def _calculate_overall_score(self, keyword_coverage: float, semantic_similarity: float, experience_alignment: float) -> int:
        """Calculate overall match score"""
        # Weighted average
        weights = {
            "keyword_coverage": 0.5,
            "semantic_similarity": 0.3,
            "experience_alignment": 0.2
        }
        
        overall_score = (
            keyword_coverage * weights["keyword_coverage"] +
            semantic_similarity * weights["semantic_similarity"] +
            experience_alignment * weights["experience_alignment"]
        )
        
        # Round to nearest integer
        return round(overall_score)