"""
Seed script to populate the database with test resumes, work history, and education.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User, Resume, WorkHistory, Education

async def create_resumes(db: AsyncSession):
    """Create test resumes with work history and education for each user."""
    # Get existing users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    if not users:
        print("No users found. Please run seed_users.py first.")
        return
    
    resumes = []
    for user in users:
        # Create 1 resume for each user
        resume = Resume(
            user_id=user.id,
            title=f"{user.username}'s Resume",
            summary=f"Experienced professional with skills in software development.",
            ats_score=80,
            feedback="Good use of keywords."
        )
        db.add(resume)
        await db.flush()
        resumes.append(resume)
        
        # Add work history entries
        work_history = WorkHistory(
            resume_id=resume.id,
            company="Tech Solutions Inc.",
            position="Senior Developer",
            start_date=datetime.now() - timedelta(days=365*2),
            end_date=datetime.now(),
            description="Led development team in creating enterprise applications."
        )
        db.add(work_history)
        
        # Add education entry
        education = Education(
            resume_id=resume.id,
            institution="University of Technology",
            degree="Bachelor of Science in Computer Science",
            start_date=datetime.now() - timedelta(days=365*6),
            end_date=datetime.now() - timedelta(days=365*2),
            description="Focused on software engineering."
        )
        db.add(education)
    
    await db.commit()
    return resumes

async def main():
    """Run the seed script for resumes."""
    async for db in get_db():
        await create_resumes(db)
        print("Resumes, work history, and education created successfully!")

if __name__ == "__main__":
    # Run the seed script
    asyncio.run(main())