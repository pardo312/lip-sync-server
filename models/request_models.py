from pydantic import BaseModel, Field
from typing import Optional

class GenerateVideoRequest(BaseModel):
    """Request model for video generation"""
    preprocess: str = Field(default="crop", description="Preprocessing method: crop, resize, full, extcrop, extfull")
    still_mode: bool = Field(default=False, description="Enable still mode for fewer head movements")
    use_enhancer: bool = Field(default=False, description="Use GFPGAN face enhancer")
    batch_size: int = Field(default=2, ge=1, le=10, description="Batch size for processing")
    size: int = Field(default=256, description="Image size (256 or 512)")
    pose_style: int = Field(default=0, ge=0, le=46, description="Pose style index")
    expression_scale: float = Field(default=1.0, ge=0.1, le=3.0, description="Expression scale factor")

class UploadFileRequest(BaseModel):
    """Request model for file uploads"""
    file_type: str = Field(description="Type of file: image or audio")
    
class TaskRequest(BaseModel):
    """Request model for task operations"""
    task_id: str = Field(description="Unique task identifier")
