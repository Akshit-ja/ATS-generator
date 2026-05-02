from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# Removed passlib dependency - using SHA256 instead
from ..database import Base

import hashlib
import secrets
# Use SHA256 with salt for password hashing (simpler, no bcrypt issues)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    generated_resumes = relationship("GeneratedResume", back_populates="user", cascade="all, delete-orphan")
    
    # Additional relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    budget_settings = relationship("UserBudgetSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    token_usage = relationship("TokenUsage", back_populates="user", cascade="all, delete-orphan")
    work_experience = relationship("WorkExperience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skills", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Documents", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("JobQueue", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def get_password_hash(cls, password: str):
        # Generate a random salt
        salt = secrets.token_hex(16)
        # Hash password with salt using SHA256
        password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"{salt}:{password_hash}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str):
        try:
            # Split salt and hash
            salt, stored_hash = hashed_password.split(':', 1)
            # Hash the plain password with the same salt
            password_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
            return password_hash == stored_hash
        except ValueError:
            return False