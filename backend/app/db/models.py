from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float, JSON, Table, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
import uuid
import enum
from datetime import datetime

Base = declarative_base()

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Association tables for many-to-many relationships
resume_skills = Table(
    'resume_skills',
    Base.metadata,
    Column('resume_id', Integer, ForeignKey('resumes.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class EndpointType(enum.Enum):
    RESUME_GENERATION = "resume_generation"
    COVER_LETTER = "cover_letter"
    JOB_ANALYSIS = "job_analysis"
    RESUME_MATCHING = "resume_matching"
    ATS_VALIDATION = "ats_validation"
    OTHER = "other"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")
    celery_tasks = relationship("CeleryTask", back_populates="user")
    token_usage = relationship("TokenUsage", back_populates="user")
    budget_settings = relationship("UserBudgetSettings", back_populates="user", uselist=False)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return _pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String)
    phone = Column(String)
    address = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    portfolio_url = Column(String)
    bio = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    ats_score = Column(Float)
    is_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    work_history = relationship("WorkHistory", back_populates="resume")
    education = relationship("Education", back_populates="resume")
    skills = relationship("Skill", secondary=resume_skills, back_populates="resumes")
    documents = relationship("Document", back_populates="resume")
    token_usage = relationship("TokenUsage", back_populates="resume")


class WorkHistory(Base):
    __tablename__ = "work_history"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)  # Null means current position
    description = Column(Text)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="work_history")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String)
    field_of_study = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)  # Null means in progress
    description = Column(Text)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String)  # e.g., "Technical", "Soft Skills", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resumes = relationship("Resume", secondary=resume_skills, back_populates="skills")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # e.g., "pdf", "docx"
    file_path = Column(String, nullable=False)  # S3 key or local path
    file_size = Column(Integer)  # Size in bytes
    storage_type = Column(String, default="local")  # "local" or "s3"
    s3_url = Column(String, nullable=True)  # S3 URL if stored in S3
    content_type = Column(String, nullable=True)  # MIME type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For signed URLs

    # Relationships
    resume = relationship("Resume", back_populates="documents")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    company = Column(String)
    description = Column(Text, nullable=False)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="job_descriptions")
    token_usage = relationship("TokenUsage", back_populates="job_description")


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    endpoint_type = Column(Enum(EndpointType), nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="token_usage")
    job_description = relationship("JobDescription", back_populates="token_usage")
    resume = relationship("Resume", back_populates="token_usage")


class UserBudgetSettings(Base):
    __tablename__ = "user_budget_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    daily_budget = Column(Float, nullable=False, default=1.0)
    monthly_budget = Column(Float, nullable=False, default=20.0)
    alert_threshold_percent = Column(Integer, nullable=False, default=80)
    alert_email_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="budget_settings")


class CeleryTask(Base):
    __tablename__ = "celery_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String, nullable=False, unique=True)
    task_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "PENDING", "SUCCESS", "FAILURE", etc.
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="celery_tasks")