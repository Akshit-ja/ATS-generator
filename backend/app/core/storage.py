"""
Storage module for handling file uploads and downloads using local filesystem.
"""
import os
from fastapi import UploadFile
from datetime import datetime, timedelta
import uuid
from typing import Optional, BinaryIO
from pathlib import Path

from app.core.config import settings

class LocalStorage:
    """Local filesystem storage implementation for file operations."""
    
    def __init__(self):
        """Initialize local storage with upload directory."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_file(self, file: UploadFile, user_id: int, file_type: str = "resume") -> str:
        """
        Upload a file to local filesystem.
        
        Args:
            file: The file to upload
            user_id: User ID for organizing files
            file_type: Type of file (resume, cover_letter, etc.)
            
        Returns:
            str: The file path for the uploaded file
        """
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".bin"
        unique_filename = f"{file_type}_{uuid.uuid4()}{file_extension}"
        
        # Create directory structure
        user_dir = self.upload_dir / f"user_{user_id}" / file_type
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # File path
        file_path = user_dir / unique_filename
        
        try:
            # Write the file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Return relative path
            return str(file_path.relative_to(self.upload_dir))
        except Exception as e:
            print(f"Error uploading file to local storage: {e}")
            raise
    
    async def upload_file_from_bytes(self, file_content: bytes, filename: str, 
                                    user_id: int, content_type: str,
                                    file_type: str = "resume") -> str:
        """
        Upload file content as bytes to local filesystem.
        
        Returns:
            str: The file path for the uploaded file
        """
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{file_type}_{uuid.uuid4()}{file_extension}"
        
        user_dir = self.upload_dir / f"user_{user_id}" / file_type
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / unique_filename
        
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            return str(file_path.relative_to(self.upload_dir))
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    def generate_presigned_url(self, file_path: str, expiration: int = 86400) -> str:
        """
        Generate a local file path (simplified for local storage).
        """
        return f"/files/{file_path}"
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local filesystem.
        """
        try:
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise

# Create a singleton instance
storage = LocalStorage()
