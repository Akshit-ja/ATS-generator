from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import UserBudgetSettings, User
from ..auth.jwt import get_current_user

router = APIRouter(
    prefix="/api/v1/budget",
    tags=["budget"],
)

class BudgetSettingsCreate(BaseModel):
    daily_budget: Optional[float] = Field(None, ge=0, description="Daily budget in USD")
    monthly_budget: Optional[float] = Field(None, ge=0, description="Monthly budget in USD")

class BudgetSettingsResponse(BaseModel):
    user_id: int
    daily_budget: Optional[float] = None
    monthly_budget: Optional[float] = None

@router.get("/", response_model=BudgetSettingsResponse)
async def get_budget_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's budget settings"""
    budget_settings = db.query(UserBudgetSettings).filter(
        UserBudgetSettings.user_id == current_user.id
    ).first()
    
    if not budget_settings:
        # Return default settings if none exist
        return BudgetSettingsResponse(
            user_id=current_user.id,
            daily_budget=None,
            monthly_budget=None,
            current_daily_usage=0.0,
            current_monthly_usage=0.0,
            created_at=None,
            updated_at=None
        )
    
    return BudgetSettingsResponse(
        user_id=budget_settings.user_id,
        daily_budget=budget_settings.daily_budget,
        monthly_budget=budget_settings.monthly_budget,
        current_daily_usage=budget_settings.current_daily_usage,
        current_monthly_usage=budget_settings.current_monthly_usage,
        created_at=budget_settings.created_at,
        updated_at=budget_settings.updated_at
    )

@router.post("/", response_model=BudgetSettingsResponse)
async def create_or_update_budget_settings(
    settings: BudgetSettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update budget settings for the current user"""
    existing_settings = db.query(UserBudgetSettings).filter(
        UserBudgetSettings.user_id == current_user.id
    ).first()
    
    if existing_settings:
        # Update existing settings
        if settings.daily_budget is not None:
            existing_settings.daily_budget = settings.daily_budget
        if settings.monthly_budget is not None:
            existing_settings.monthly_budget = settings.monthly_budget
        
        db.commit()
        db.refresh(existing_settings)
        
        return BudgetSettingsResponse(
            user_id=existing_settings.user_id,
            daily_budget=existing_settings.daily_budget,
            monthly_budget=existing_settings.monthly_budget,
            current_daily_usage=existing_settings.current_daily_usage,
            current_monthly_usage=existing_settings.current_monthly_usage,
            created_at=existing_settings.created_at,
            updated_at=existing_settings.updated_at
        )
    else:
        # Create new settings
        new_settings = UserBudgetSettings(
            user_id=current_user.id,
            daily_budget=settings.daily_budget,
            monthly_budget=settings.monthly_budget
        )
        
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
        
        return BudgetSettingsResponse(
            user_id=new_settings.user_id,
            daily_budget=new_settings.daily_budget,
            monthly_budget=new_settings.monthly_budget,
            current_daily_usage=new_settings.current_daily_usage,
            current_monthly_usage=new_settings.current_monthly_usage,
            created_at=new_settings.created_at,
            updated_at=new_settings.updated_at
        )

@router.delete("/")
async def delete_budget_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete budget settings for the current user"""
    existing_settings = db.query(UserBudgetSettings).filter(
        UserBudgetSettings.user_id == current_user.id
    ).first()
    
    if not existing_settings:
        raise HTTPException(
            status_code=404, 
            detail="Budget settings not found"
        )
    
    db.delete(existing_settings)
    db.commit()
    
    return {"message": "Budget settings deleted successfully"}

@router.delete("/settings")
async def reset_budget_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset (delete) the current user's budget settings"""
    existing_settings = db.query(UserBudgetSettings).filter(
        UserBudgetSettings.user_id == current_user.id
    ).first()
    
    if existing_settings:
        db.delete(existing_settings)
        db.commit()
    
    return {"message": "Budget settings reset successfully"}