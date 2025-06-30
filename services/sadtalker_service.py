import os
import sys
import torch
import asyncio
import logging
from typing import Optional
from pathlib import Path

# Import SadTalker - PYTHONPATH is set in Dockerfile to include /app/SadTalker
from src.gradio_demo import SadTalker

logger = logging.getLogger(__name__)

class SadTalkerService:
    """Service wrapper for SadTalker functionality"""
    
    def __init__(self):
        self.sadtalker = None
        self.device = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the SadTalker service"""
        try:
            logger.info("Initializing SadTalker service...")
            
            # Determine device
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("Using GPU for inference")
            else:
                self.device = "cpu"
                logger.info("Using CPU for inference")
            
            # Initialize SadTalker with paths from environment variables
            sadtalker_base = os.getenv('SADTALKER_PATH', '/app/SadTalker')
            checkpoint_path = os.path.join(sadtalker_base, 'checkpoints')
            config_path = os.path.join(sadtalker_base, 'src', 'config')
            
            # Ensure paths exist
            if not os.path.exists(checkpoint_path):
                raise FileNotFoundError(f"Checkpoints directory not found: {checkpoint_path}")
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config directory not found: {config_path}")
            
            self.sadtalker = SadTalker(
                checkpoint_path=checkpoint_path,
                config_path=config_path,
                lazy_load=True
            )
            
            self.initialized = True
            logger.info("SadTalker service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SadTalker service: {str(e)}")
            raise
    
    def is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        return torch.cuda.is_available()
    
    async def generate_video(
        self,
        source_image_path: str,
        audio_path: str,
        preprocess: str = "crop",
        still_mode: bool = False,
        use_enhancer: bool = False,
        batch_size: int = 2,
        size: int = 256,
        pose_style: int = 0,
        expression_scale: float = 1.0,
        result_dir: str = "./results/"
    ) -> str:
        """
        Generate talking head video
        
        Args:
            source_image_path: Path to source image
            audio_path: Path to audio file
            preprocess: Preprocessing method
            still_mode: Enable still mode
            use_enhancer: Use face enhancer
            batch_size: Batch size for processing
            size: Image size (256 or 512)
            pose_style: Pose style index
            expression_scale: Expression scale factor
            result_dir: Directory to save results
            
        Returns:
            Path to generated video file
        """
        if not self.initialized:
            raise RuntimeError("SadTalker service not initialized")
        
        try:
            logger.info(f"Generating video from image: {source_image_path}, audio: {audio_path}")
            
            # Ensure result directory exists
            os.makedirs(result_dir, exist_ok=True)
            
            # Run SadTalker generation in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            result_path = await loop.run_in_executor(
                None,
                self._generate_video_sync,
                source_image_path,
                audio_path,
                preprocess,
                still_mode,
                use_enhancer,
                batch_size,
                size,
                pose_style,
                expression_scale,
                result_dir
            )
            
            logger.info(f"Video generation completed: {result_path}")
            return result_path
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise
    
    def _generate_video_sync(
        self,
        source_image_path: str,
        audio_path: str,
        preprocess: str,
        still_mode: bool,
        use_enhancer: bool,
        batch_size: int,
        size: int,
        pose_style: int,
        expression_scale: float,
        result_dir: str
    ) -> str:
        """Synchronous video generation method"""
        try:
            result_path = self.sadtalker.test(
                source_image=source_image_path,
                driven_audio=audio_path,
                preprocess=preprocess,
                still_mode=still_mode,
                use_enhancer=use_enhancer,
                batch_size=batch_size,
                size=size,
                pose_style=pose_style,
                exp_scale=expression_scale,
                result_dir=result_dir
            )
            
            return result_path
            
        except Exception as e:
            logger.error(f"Synchronous video generation failed: {str(e)}")
            raise
    
    def validate_inputs(self, source_image_path: str, audio_path: str) -> bool:
        """Validate input files"""
        try:
            # Check if files exist
            if not os.path.exists(source_image_path):
                raise FileNotFoundError(f"Source image not found: {source_image_path}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Check file extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            audio_extensions = ['.wav', '.mp3', '.m4a', '.flac']
            
            image_ext = Path(source_image_path).suffix.lower()
            audio_ext = Path(audio_path).suffix.lower()
            
            if image_ext not in image_extensions:
                raise ValueError(f"Unsupported image format: {image_ext}")
            
            if audio_ext not in audio_extensions:
                raise ValueError(f"Unsupported audio format: {audio_ext}")
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            raise
    
    def cleanup_resources(self):
        """Clean up GPU memory and resources"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            import gc
            gc.collect()
            
            logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Resource cleanup failed: {str(e)}")
