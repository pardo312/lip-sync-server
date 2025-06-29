# SadTalker Lip-Sync API

A FastAPI-based web service that provides AI-powered talking head video generation using SadTalker technology. This API allows you to create realistic lip-sync videos by combining a source image with an audio file.

## Features

- 🎭 **AI-Powered Lip Sync**: Generate realistic talking head videos from static images
- 🚀 **FastAPI Backend**: High-performance async API with automatic documentation
- 🎨 **Multiple Preprocessing Options**: Support for different image preprocessing methods
- 🔧 **Customizable Parameters**: Fine-tune expression scale, pose style, and more
- 📁 **File Management**: Secure file upload and download system
- 🎯 **Task Management**: Asynchronous video generation with status tracking
- 🖥️ **GPU Support**: Automatic GPU detection and utilization when available
- 📊 **Health Monitoring**: Built-in health check endpoints
- 🌐 **CORS Enabled**: Ready for web frontend integration

## Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for faster processing)
- SadTalker model checkpoints and configuration files

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lip-sync-app
   ```

2. **Install PyTorch with CUDA support** (if you have a compatible GPU)
   ```bash
   # For CUDA 11.8
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # For CUDA 12.1
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   # For CPU only
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up SadTalker**
   - Ensure you have the SadTalker source code in the parent directory
   - Download the required model checkpoints to the `checkpoints/` directory
   - Verify the configuration files are in the `src/config/` directory

## Project Structure

```
lip-sync-app/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── request_models.py   # API request models
│   └── response_models.py  # API response models
├── services/               # Business logic
│   ├── __init__.py
│   └── sadtalker_service.py # SadTalker integration service
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── file_handler.py     # File upload/download handling
│   └── validation.py       # Input validation utilities
├── uploads/                # Temporary file storage (created at runtime)
├── results/                # Generated video storage (created at runtime)
└── temp/                   # Temporary processing files (created at runtime)
```

## Usage

### Starting the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

### Basic API Endpoints

#### Health Check
```http
GET /api/v1/health
```

#### Upload Files
```http
POST /api/v1/upload/image
POST /api/v1/upload/audio
```

#### Generate Video
```http
POST /api/v1/generate
```

#### Check Task Status
```http
GET /api/v1/status/{task_id}
```

#### Download Generated Video
```http
GET /api/v1/download/{task_id}
```

### Example Usage with cURL

1. **Generate a video directly**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/generate" \
        -H "Content-Type: multipart/form-data" \
        -F "source_image=@path/to/your/image.jpg" \
        -F "driven_audio=@path/to/your/audio.wav" \
        -F "preprocess=crop" \
        -F "still_mode=false" \
        -F "use_enhancer=true"
   ```

2. **Check task status**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/status/{task_id}"
   ```

3. **Download the result**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/download/{task_id}" \
        -o generated_video.mp4
   ```

## Configuration Parameters

### Video Generation Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preprocess` | string | "crop" | Preprocessing method: crop, resize, full, extcrop, extfull |
| `still_mode` | boolean | false | Enable still mode for fewer head movements |
| `use_enhancer` | boolean | false | Use GFPGAN face enhancer for better quality |
| `batch_size` | integer | 2 | Batch size for processing (1-10) |
| `size` | integer | 256 | Image size (256 or 512) |
| `pose_style` | integer | 0 | Pose style index (0-46) |
| `expression_scale` | float | 1.0 | Expression scale factor (0.1-3.0) |

### Supported File Formats

**Images**: JPG, JPEG, PNG, BMP, TIFF
**Audio**: WAV, MP3, M4A, FLAC

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

You can configure the following environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

### Adding New Features

1. **Models**: Add new Pydantic models in the `models/` directory
2. **Services**: Implement business logic in the `services/` directory
3. **Utilities**: Add helper functions in the `utils/` directory
4. **Endpoints**: Add new API endpoints in `main.py`

## Performance Considerations

- **GPU Usage**: The application automatically detects and uses GPU when available
- **Memory Management**: Automatic cleanup of GPU memory after processing
- **Async Processing**: Video generation runs in background tasks
- **File Cleanup**: Temporary files are managed automatically

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch_size parameter
   - Use smaller image size (256 instead of 512)
   - Ensure no other GPU processes are running

2. **Model Loading Errors**
   - Verify SadTalker checkpoints are properly downloaded
   - Check that config files are in the correct location
   - Ensure file paths in the service are correct

3. **File Upload Issues**
   - Check file format compatibility
   - Verify file size limits
   - Ensure proper permissions on upload directories

### Logging

The application uses structured logging. Check the console output for detailed error messages and processing status.

## API Response Examples

### Successful Video Generation
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Video generation started"
}
```

### Task Status Response
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "message": "Video generation completed successfully",
  "created_at": "2024-01-01T12:00:00",
  "download_url": "/api/v1/download/123e4567-e89b-12d3-a456-426614174000"
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "gpu_available": true,
  "version": "1.0.0"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [SadTalker](https://github.com/OpenTalker/SadTalker) - The underlying AI model for talking head generation
- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [PyTorch](https://pytorch.org/) - Deep learning framework

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Open an issue in the repository

---

**Note**: This API requires the SadTalker model and checkpoints to be properly installed and configured. Please refer to the original SadTalker repository for model setup instructions.
