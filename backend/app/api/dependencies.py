from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..auth.jwt import get_current_active_user
from ..auth.models import User
from ..database import get_db
import time
from typing import Dict, Optional
import redis
from fastapi import Request

# Initialize Redis client for rate limiting
try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
except:
    # Fallback if Redis is not available
    redis_client = None
    print("Warning: Redis not available. Rate limiting will be disabled.")

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 10  # Number of requests allowed
RATE_LIMIT_WINDOW = 60    # Time window in seconds (1 minute)

def get_current_user_dependency(db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user
    """
    def get_user(current_user: User = Depends(get_current_active_user)):
        return current_user
    return get_user

def rate_limit_dependency(tier: str = "free"):
    """
    Rate limiting middleware using Redis sliding window
    Different tiers can have different rate limits
    """
    async def rate_limit(request: Request, current_user: User = Depends(get_current_active_user)):
        if not redis_client:
            # Skip rate limiting if Redis is not available
            return
            
        # Set tier-specific limits
        limits = {
            "free": {"requests": 10, "window": 60},
            "premium": {"requests": 30, "window": 60},
            "enterprise": {"requests": 100, "window": 60}
        }
        
        # Default to free tier if specified tier doesn't exist
        limit_config = limits.get(tier, limits["free"])
        
        # Create a unique key for each user
        key = f"rate_limit:{current_user.id}:{request.url.path}"
        
        # Get current timestamp
        now = time.time()
        
        # Add current request to the sorted set with score as current timestamp
        redis_client.zadd(key, {str(now): now})
        
        # Remove requests outside the current window
        redis_client.zremrangebyscore(key, 0, now - limit_config["window"])
        
        # Count requests in the current window
        request_count = redis_client.zcard(key)
        
        # Set key expiration
        redis_client.expire(key, limit_config["window"])
        
        # Check if rate limit is exceeded
        if request_count > limit_config["requests"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {limit_config['window']} seconds."
            )
            
    return rate_limit

def verify_resume_ownership(db: Session = Depends(get_db)):
    """
    Dependency to verify that a user owns a resume
    """
    def verify(resume_id: int, current_user: User = Depends(get_current_active_user)):
        from ..models.resume import Resume
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or you don't have permission to access it"
            )
        return resume
    return verify

def verify_job_description_ownership(db: Session = Depends(get_db)):
    """
    Dependency to verify that a user owns a job description
    """
    def verify(job_id: int, current_user: User = Depends(get_current_active_user)):
        from ..models.resume import JobDescription
        job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found or you don't have permission to access it"
            )
        return job
    return verify

def verify_generated_resume_ownership(db: Session = Depends(get_db)):
    """
    Dependency to verify that a user owns a generated resume
    """
    def verify(generated_id: int, current_user: User = Depends(get_current_active_user)):
        from ..models.resume import GeneratedResume
        generated = db.query(GeneratedResume).filter(
            GeneratedResume.id == generated_id, 
            GeneratedResume.user_id == current_user.id
        ).first()
        if not generated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated resume not found or you don't have permission to access it"
            )
        return generated
    return verify