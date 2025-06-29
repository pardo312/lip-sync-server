import os
import shutil
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file upload, storage, and management"""
    
    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 100 * 1024 * 1024):  # 100MB
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.image_dir = os.path.join(upload_dir, "images")
        self.audio_dir = os.path.join(upload_dir, "audio")
        
        # Create directories
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def save_upload(self, file: UploadFile, file_id: str, file_type: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file: FastAPI UploadFile object
            file_id: Unique identifier for the file
            file_type: Type of file ('image' or 'audio')
            
        Returns:
            Path to saved file
        """
        try:
            # Validate file size
            if hasattr(file, 'size') and file.size > self.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
            
            # Determine save directory
            if file_type == "image":
                save_dir = self.image_dir
            elif file_type == "audio":
                save_dir = self.audio_dir
            else:
                raise ValueError(f"Invalid file type: {file_type}")
            
            # Get file extension
            file_extension = Path(file.filename).suffix if file.filename else ""
            
            # Create filename
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join(save_dir, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from disk
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "path": file_path,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": Path(file_path).suffix
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old uploaded files
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > max_age_seconds:
                        self.delete_file(file_path)
                        logger.info(f"Cleaned up old file: {file_path}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {str(e)}")
    
    def get_upload_stats(self) -> dict:
        """
        Get statistics about uploaded files
        
        Returns:
            Dictionary with upload statistics
        """
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "image_files": 0,
                "audio_files": 0,
                "image_size": 0,
                "audio_size": 0
            }
            
            # Count image files
            if os.path.exists(self.image_dir):
                for file in os.listdir(self.image_dir):
                    file_path = os.path.join(self.image_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        stats["image_files"] += 1
                        stats["image_size"] += size
            
            # Count audio files
            if os.path.exists(self.audio_dir):
                for file in os.listdir(self.audio_dir):
                    file_path = os.path.join(self.audio_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        stats["audio_files"] += 1
                        stats["audio_size"] += size
            
            stats["total_files"] = stats["image_files"] + stats["audio_files"]
            stats["total_size"] = stats["image_size"] + stats["audio_size"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get upload stats: {str(e)}")
            return {}
