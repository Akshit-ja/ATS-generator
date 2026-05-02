"""
Seed script to populate the database with test users and profiles.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.database import get_db
from app.db.models import User, UserProfile

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_users(db: AsyncSession):
    """Create 3 test users with profiles."""
    test_users = [
        ("john@example.com", "johndoe", "John Doe"),
        ("jane@example.com", "janedoe", "Jane Doe"),
        ("bob@example.com", "bobsmith", "Bob Smith")
    ]
    
    users = []
    for email, username, fullname in test_users:
        user = User(
            email=email,
            username=username,
            hashed_password=pwd_context.hash("password123"),
            is_active=True
        )
        db.add(user)
        await db.flush()
        
        profile = UserProfile(
            user_id=user.id,
            full_name=fullname,
            phone=f"555-{len(username)}{len(email)}",
            address=f"{len(username)*100} Main St, Anytown, USA",
            linkedin_url=f"https://linkedin.com/in/{username}",
            github_url=f"https://github.com/{username}",
            portfolio_url=f"https://{username}.dev",
            bio=f"Professional with experience in software development."
        )
        db.add(profile)
        users.append(user)
    
    await db.commit()
    return users

async def main():
    """Run the seed script for users."""
    async for db in get_db():
        await create_users(db)
        print("Users and profiles created successfully!")

if __name__ == "__main__":
    # Run the seed script
    asyncio.run(main())