"""
Seed script to populate the database with skills and documents.
"""
import asyncio
import base64
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User, Resume, Skill, Document

# Sample skills for resumes
SKILLS = [
    "Python", "JavaScript", "React", "Node.js", "SQL", 
    "Docker", "AWS", "Git", "TypeScript", "FastAPI",
    "Communication", "Project Management", "Team Leadership"
]

async def create_skills_and_documents(db: AsyncSession):
    """Create skills and documents for existing resumes."""
    # Get existing resumes
    result = await db.execute(select(Resume))
    resumes = result.scalars().all()
    
    if not resumes:
        print("No resumes found. Please run seed_resumes.py first.")
        return
    
    # Create skills (global pool)
    skills = []
    for skill_name in SKILLS:
        skill = Skill(name=skill_name)
        db.add(skill)
        skills.append(skill)
    
    await db.flush()
    
    # Associate skills with resumes
    for resume in resumes:
        # Assign 5-7 random skills to each resume
        for i, skill in enumerate(skills):
            if i % 2 == 0 or i < 7:  # Simple way to select some skills
                await db.execute(
                    "INSERT INTO resume_skills (resume_id, skill_id) VALUES (:resume_id, :skill_id)",
                    {"resume_id": resume.id, "skill_id": skill.id}
                )
        
        # Create a document for each resume
        document = Document(
            user_id=resume.user_id,
            resume_id=resume.id,
            filename=f"{resume.title.replace(' ', '_')}.pdf",
            content_type="application/pdf",
            file_size=12345,  # Dummy size
            file_path=f"/uploads/{resume.user_id}/{resume.id}.pdf",
            file_content=base64.b64encode(b"Sample PDF content").decode('utf-8')  # Dummy content
        )
        db.add(document)
    
    await db.commit()

async def main():
    """Run the seed script for skills and documents."""
    async for db in get_db():
        await create_skills_and_documents(db)
        print("Skills and documents created successfully!")

if __name__ == "__main__":
    # Run the seed script
    asyncio.run(main())