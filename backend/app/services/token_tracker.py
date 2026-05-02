from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
import tiktoken
from typing import Dict, Optional, List, Any
import logging

from ..models import TokenUsage, User, JobDescription, Resume, UserBudgetSettings, EndpointType

logger = logging.getLogger(__name__)

# OpenAI pricing per 1K tokens (as of 2023)
MODEL_PRICING = {
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
    "default": {"input": 0.01, "output": 0.03}  # Default fallback pricing
}

class TokenTracker:
    """Service to track OpenAI API token usage and costs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in a text string using tiktoken"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {str(e)}. Using approximate count.")
            # Fallback: approximate token count (1 token ≈ 4 chars in English)
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost based on token count and model pricing"""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def track_usage_from_response(
        self, 
        response: Dict[str, Any],
        user_id: int,
        endpoint_type: EndpointType,
        job_id: Optional[int] = None,
        resume_id: Optional[int] = None
    ) -> TokenUsage:
        """Track token usage from an OpenAI API response"""
        try:
            # Extract usage data from OpenAI response
            usage = response.get("usage", {})
            model = response.get("model", "default")
            
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
            
            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, model)
            
            # Record usage in database
            return self.record_usage(
                user_id=user_id,
                endpoint_type=endpoint_type,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost,
                job_id=job_id,
                resume_id=resume_id
            )
        except Exception as e:
            logger.error(f"Error tracking token usage: {str(e)}")
            # Create minimal record in case of error
            return self.record_usage(
                user_id=user_id,
                endpoint_type=endpoint_type,
                model="unknown",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost=0,
                job_id=job_id,
                resume_id=resume_id
            )
    
    def record_usage(
        self,
        user_id: int,
        endpoint_type: EndpointType,
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        cost: float,
        job_id: Optional[int] = None,
        resume_id: Optional[int] = None
    ) -> TokenUsage:
        """Record token usage in the database"""
        token_usage = TokenUsage(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            endpoint_type=endpoint_type,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(token_usage)
        self.db.commit()
        self.db.refresh(token_usage)
        
        # Check budget alerts
        self.check_budget_alerts(user_id)
        
        return token_usage
    
    def check_budget_alerts(self, user_id: int) -> None:
        """Check if user has exceeded budget thresholds and log alerts"""
        # Get user budget settings
        budget_settings = self.db.query(UserBudgetSettings).filter(
            UserBudgetSettings.user_id == user_id
        ).first()
        
        if not budget_settings:
            return  # No budget settings to check
        
        # Get today's date
        today = date.today()
        
        # Calculate daily usage
        daily_usage = self.db.query(TokenUsage).filter(
            TokenUsage.user_id == user_id,
            TokenUsage.timestamp >= datetime.combine(today, datetime.min.time())
        ).with_entities(
            func.sum(TokenUsage.cost).label("total_cost")
        ).scalar() or 0.0
        
        # Calculate monthly usage (current month)
        first_day = date(today.year, today.month, 1)
        monthly_usage = self.db.query(TokenUsage).filter(
            TokenUsage.user_id == user_id,
            TokenUsage.timestamp >= datetime.combine(first_day, datetime.min.time())
        ).with_entities(
            func.sum(TokenUsage.cost).label("total_cost")
        ).scalar() or 0.0
        
        # Check daily budget
        if budget_settings.daily_budget and daily_usage >= budget_settings.daily_budget:
            logger.warning(f"User {user_id} has exceeded daily budget: ${daily_usage:.2f} / ${budget_settings.daily_budget:.2f}")
            # Here you could trigger notifications, emails, etc.
        
        # Check daily warning threshold (80% of budget)
        elif budget_settings.daily_budget and daily_usage >= (budget_settings.daily_budget * 0.8):
            logger.info(f"User {user_id} is approaching daily budget: ${daily_usage:.2f} / ${budget_settings.daily_budget:.2f}")
        
        # Check monthly budget
        if budget_settings.monthly_budget and monthly_usage >= budget_settings.monthly_budget:
            logger.warning(f"User {user_id} has exceeded monthly budget: ${monthly_usage:.2f} / ${budget_settings.monthly_budget:.2f}")
            # Here you could trigger notifications, emails, etc.
        
        # Check monthly warning threshold (80% of budget)
        elif budget_settings.monthly_budget and monthly_usage >= (budget_settings.monthly_budget * 0.8):
            logger.info(f"User {user_id} is approaching monthly budget: ${monthly_usage:.2f} / ${budget_settings.monthly_budget:.2f}")