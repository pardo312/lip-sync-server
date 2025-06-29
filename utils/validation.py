import os
from pathlib import Path
from typing import List
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

# Supported file formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg']

# File size limits (in bytes)
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB

def validate_image(file: UploadFile) -> bool:
    """
    Validate uploaded image file
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check if file exists
        if not file or not file.filename:
            logger.error("No file provided")
            return False
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in SUPPORTED_IMAGE_FORMATS:
            logger.error(f"Unsupported image format: {file_extension}")
            return False
        
        # Check file size if available
        if hasattr(file, 'size') and file.size:
            if file.size > MAX_IMAGE_SIZE:
                logger.error(f"Image file too large: {file.size} bytes (max: {MAX_IMAGE_SIZE})")
                return False
            
            if file.size == 0:
                logger.error("Empty image file")
                return False
        
        # Check content type if available
        if hasattr(file, 'content_type') and file.content_type:
            valid_content_types = [
                'image/jpeg', 'image/jpg', 'image/png', 
                'image/bmp', 'image/tiff', 'image/webp'
            ]
            if file.content_type not in valid_content_types:
                logger.warning(f"Unexpected content type for image: {file.content_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return False

def validate_audio(file: UploadFile) -> bool:
    """
    Validate uploaded audio file
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check if file exists
        if not file or not file.filename:
            logger.error("No file provided")
            return False
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in SUPPORTED_AUDIO_FORMATS:
            logger.error(f"Unsupported audio format: {file_extension}")
            return False
        
        # Check file size if available
        if hasattr(file, 'size') and file.size:
            if file.size > MAX_AUDIO_SIZE:
                logger.error(f"Audio file too large: {file.size} bytes (max: {MAX_AUDIO_SIZE})")
                return False
            
            if file.size == 0:
                logger.error("Empty audio file")
                return False
        
        # Check content type if available
        if hasattr(file, 'content_type') and file.content_type:
            valid_content_types = [
                'audio/wav', 'audio/wave', 'audio/x-wav',
                'audio/mpeg', 'audio/mp3',
                'audio/mp4', 'audio/m4a',
                'audio/flac', 'audio/x-flac',
                'audio/aac', 'audio/ogg'
            ]
            if file.content_type not in valid_content_types:
                logger.warning(f"Unexpected content type for audio: {file.content_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"Audio validation failed: {str(e)}")
        return False

def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is accessible
    
    Args:
        file_path: Path to file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if not file_path:
            return False
        
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            logger.error(f"File is not readable: {file_path}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"File path validation failed: {str(e)}")
        return False

def validate_generation_parameters(
    preprocess: str,
    batch_size: int,
    size: int,
    pose_style: int,
    expression_scale: float
) -> bool:
    """
    Validate video generation parameters
    
    Args:
        preprocess: Preprocessing method
        batch_size: Batch size
        size: Image size
        pose_style: Pose style index
        expression_scale: Expression scale factor
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Validate preprocess method
        valid_preprocess = ['crop', 'resize', 'full', 'extcrop', 'extfull']
        if preprocess not in valid_preprocess:
            logger.error(f"Invalid preprocess method: {preprocess}")
            return False
        
        # Validate batch size
        if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 10:
            logger.error(f"Invalid batch size: {batch_size} (must be 1-10)")
            return False
        
        # Validate image size
        valid_sizes = [256, 512]
        if size not in valid_sizes:
            logger.error(f"Invalid image size: {size} (must be 256 or 512)")
            return False
        
        # Validate pose style
        if not isinstance(pose_style, int) or pose_style < 0 or pose_style > 46:
            logger.error(f"Invalid pose style: {pose_style} (must be 0-46)")
            return False
        
        # Validate expression scale
        if not isinstance(expression_scale, (int, float)) or expression_scale < 0.1 or expression_scale > 3.0:
            logger.error(f"Invalid expression scale: {expression_scale} (must be 0.1-3.0)")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Parameter validation failed: {str(e)}")
        return False

def get_file_info(file: UploadFile) -> dict:
    """
    Get information about an uploaded file
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Dictionary with file information
    """
    try:
        info = {
            "filename": file.filename,
            "content_type": getattr(file, 'content_type', None),
            "size": getattr(file, 'size', None),
            "extension": Path(file.filename).suffix.lower() if file.filename else None
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get file info: {str(e)}")
        return {}

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    try:
        if not filename:
            return "unnamed_file"
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
        
    except Exception as e:
        logger.error(f"Filename sanitization failed: {str(e)}")
        return "unnamed_file"
