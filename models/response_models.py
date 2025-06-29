from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GenerateVideoResponse(BaseModel):
    """Response model for video generation requests"""
    task_id: str = Field(description="Unique task identifier")
    status: str = Field(description="Task status: queued, processing, completed, failed")
    message: str = Field(description="Status message")
    created_at: Optional[datetime] = Field(default=None, description="Task creation timestamp")

class TaskStatusResponse(BaseModel):
    """Response model for task status queries"""
    task_id: str = Field(description="Unique task identifier")
    status: str = Field(description="Task status: queued, processing, completed, failed")
    message: str = Field(description="Status message")
    created_at: datetime = Field(description="Task creation timestamp")
    download_url: Optional[str] = Field(default=None, description="Download URL when completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Health check timestamp")
    gpu_available: bool = Field(description="Whether GPU is available")
    version: str = Field(description="API version")

class UploadResponse(BaseModel):
    """Response model for file uploads"""
    file_id: str = Field(description="Unique file identifier")
    filename: str = Field(description="Original filename")
    path: str = Field(description="File storage path")
    file_type: str = Field(description="File type: image or audio")
    size: int = Field(description="File size in bytes")

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
