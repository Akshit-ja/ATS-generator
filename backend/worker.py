#!/usr/bin/env python
"""
Celery worker startup script for resume generation tasks.
Run this script to start the Celery worker that processes resume generation tasks.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable not set!")
    print("Set this variable before running the worker.")

# Import the Celery app
from app.celery_config import celery_app

if __name__ == "__main__":
    # Start the Celery worker
    celery_app.worker_main(["worker", "--loglevel=info", "-Q", "resume_generation"])