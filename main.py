from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import uuid
import shutil
from pathlib import Path
import logging
from typing import Optional
import asyncio
from datetime import datetime

from models.request_models import GenerateVideoRequest
from models.response_models import GenerateVideoResponse, TaskStatusResponse, HealthResponse
from services.sadtalker_service import SadTalkerService
from utils.file_handler import FileHandler
from utils.validation import validate_image, validate_audio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SadTalker API",
    description="AI-powered talking head video generation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
sadtalker_service = SadTalkerService()
file_handler = FileHandler()

# In-memory task storage (in production, use Redis or database)
tasks = {}

@app.on_startup
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting SadTalker API...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Initialize SadTalker service
    await sadtalker_service.initialize()
    logger.info("SadTalker API started successfully!")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SadTalker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        gpu_available = sadtalker_service.is_gpu_available()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            gpu_available=gpu_available,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/api/v1/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload source image"""
    try:
        # Validate image
        if not validate_image(file):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = await file_handler.save_upload(file, file_id, "image")
        
        return {"file_id": file_id, "filename": file.filename, "path": file_path}
    
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/v1/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file"""
    try:
        # Validate audio
        if not validate_audio(file):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = await file_handler.save_upload(file, file_id, "audio")
        
        return {"file_id": file_id, "filename": file.filename, "path": file_path}
    
    except Exception as e:
        logger.error(f"Audio upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def generate_video_task(task_id: str, source_image_path: str, audio_path: str, options: dict):
    """Background task for video generation"""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["message"] = "Generating video..."
        
        # Generate video using SadTalker
        result_path = await sadtalker_service.generate_video(
            source_image_path, 
            audio_path, 
            **options
        )
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result_path"] = result_path
        tasks[task_id]["message"] = "Video generation completed successfully"
        
    except Exception as e:
        logger.error(f"Video generation failed for task {task_id}: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["message"] = f"Video generation failed: {str(e)}"

@app.post("/api/v1/generate", response_model=GenerateVideoResponse)
async def generate_video(
    background_tasks: BackgroundTasks,
    source_image: UploadFile = File(...),
    driven_audio: UploadFile = File(...),
    preprocess: str = "crop",
    still_mode: bool = False,
    use_enhancer: bool = False,
    batch_size: int = 2,
    size: int = 256,
    pose_style: int = 0,
    expression_scale: float = 1.0
):
    """Generate talking head video from image and audio"""
    try:
        # Validate inputs
        if not validate_image(source_image):
            raise HTTPException(status_code=400, detail="Invalid source image")
        
        if not validate_audio(driven_audio):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        
        # Create task
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            "status": "queued",
            "created_at": datetime.now(),
            "message": "Task queued for processing"
        }
        
        # Save uploaded files
        image_id = str(uuid.uuid4())
        audio_id = str(uuid.uuid4())
        
        image_path = await file_handler.save_upload(source_image, image_id, "image")
        audio_path = await file_handler.save_upload(driven_audio, audio_id, "audio")
        
        # Prepare options
        options = {
            "preprocess": preprocess,
            "still_mode": still_mode,
            "use_enhancer": use_enhancer,
            "batch_size": batch_size,
            "size": size,
            "pose_style": pose_style,
            "expression_scale": expression_scale
        }
        
        # Start background task
        background_tasks.add_task(
            generate_video_task, 
            task_id, 
            image_path, 
            audio_path, 
            options
        )
        
        return GenerateVideoResponse(
            task_id=task_id,
            status="queued",
            message="Video generation started"
        )
        
    except Exception as e:
        logger.error(f"Generate video request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

@app.get("/api/v1/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a video generation task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        message=task.get("message", ""),
        created_at=task["created_at"]
    )
    
    if task["status"] == "completed":
        response.download_url = f"/api/v1/download/{task_id}"
    elif task["status"] == "failed":
        response.error = task.get("error", "Unknown error")
    
    return response

@app.get("/api/v1/download/{task_id}")
async def download_video(task_id: str):
    """Download the generated video"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video not ready for download")
    
    result_path = task.get("result_path")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        result_path,
        media_type="video/mp4",
        filename=f"sadtalker_result_{task_id}.mp4"
    )

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its associated files"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    # Clean up files
    if "result_path" in task and os.path.exists(task["result_path"]):
        os.remove(task["result_path"])
    
    # Remove task from memory
    del tasks[task_id]
    
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
