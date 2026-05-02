"""
Seed script to populate the database with job descriptions and celery tasks.
"""
import asyncio
import json
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User, JobDescription, CeleryTask

async def create_jobs_and_tasks(db: AsyncSession):
    """Create job descriptions and celery tasks for existing users."""
    # Get existing users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    if not users:
        print("No users found. Please run seed_users.py first.")
        return
    
    # Create job descriptions and tasks
    for user in users:
        # Create job description
        job = JobDescription(
            user_id=user.id,
            title="Senior Software Engineer",
            company="Tech Innovations Inc.",
            description="Looking for a Senior Software Engineer with Python and JavaScript experience.",
            analysis=json.dumps({
                "keywords": ["Python", "JavaScript"],
                "match_score": 85
            })
        )
        db.add(job)
        
        # Create a celery task
        task = CeleryTask(
            user_id=user.id,
            task_id=str(uuid.uuid4()),
            task_name="resume_analysis",
            status="completed",
            result=json.dumps({"message": "Task completed successfully"}),
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        db.add(task)
    
    await db.commit()

async def main():
    """Run the seed script for job descriptions and celery tasks."""
    async for db in get_db():
        await create_jobs_and_tasks(db)
        print("Job descriptions and celery tasks created successfully!")

if __name__ == "__main__":
    # Run the seed script
    asyncio.run(main())