# SadTalker FastAPI Docker Setup

This Docker setup provides a containerized environment for running the SadTalker FastAPI application with GPU support and runtime model downloads.

## Prerequisites

1. **Docker** and **Docker Compose** installed
2. **NVIDIA Docker runtime** for GPU support:
   ```bash
   # Install nvidia-docker2
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f sadtalker-api
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t sadtalker-fastapi .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name sadtalker-api \
     --gpus all \
     -p 8000:8000 \
     -v $(pwd)/docker-volumes/checkpoints:/app/SadTalker/checkpoints \
     -v $(pwd)/docker-volumes/gfpgan-weights:/app/SadTalker/gfpgan/weights \
     -v $(pwd)/docker-volumes/uploads:/app/uploads \
     -v $(pwd)/docker-volumes/results:/app/results \
     sadtalker-fastapi
   ```

## First Startup

On the first startup, the container will:

1. **Check for existing models** in the mounted volumes
2. **Download missing models** using the official SadTalker download script:
   - Main SadTalker models (~2-3GB)
   - GFPGAN enhancer models (~500MB)
3. **Start the FastAPI server** on port 8000

**Note:** The first startup may take 10-15 minutes depending on your internet connection.

## Model Downloads

The container automatically downloads these models at runtime:

### Main SadTalker Models
- `mapping_00109-model.pth.tar`
- `mapping_00229-model.pth.tar`
- `SadTalker_V0.0.2_256.safetensors`
- `SadTalker_V0.0.2_512.safetensors`

### GFPGAN Enhancer Models
- `alignment_WFLW_4HG.pth`
- `detection_Resnet50_Final.pth`
- `GFPGANv1.4.pth`
- `parsing_parsenet.pth`

## Volume Mounts

The following directories are mounted as volumes for persistence:

```
./docker-volumes/checkpoints     → /app/SadTalker/checkpoints
./docker-volumes/gfpgan-weights  → /app/SadTalker/gfpgan/weights
./docker-volumes/uploads         → /app/uploads
./docker-volumes/results         → /app/results
./docker-volumes/temp            → /app/temp
```

## API Endpoints

Once running, the API will be available at `http://localhost:8000`:

- **API Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/api/v1/health`
- **Generate Video:** `POST http://localhost:8000/api/v1/generate`

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Generate Video
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: multipart/form-data" \
  -F "source_image=@path/to/image.jpg" \
  -F "driven_audio=@path/to/audio.wav" \
  -F "use_enhancer=true"
```

## Troubleshooting

### Container won't start
1. Check if NVIDIA Docker runtime is installed
2. Verify GPU availability: `nvidia-smi`
3. Check container logs: `docker-compose logs sadtalker-api`

### Models not downloading
1. Check internet connectivity inside container
2. Verify volume mounts are correct
3. Check available disk space

### Out of memory errors
1. Reduce batch_size parameter
2. Use smaller image size (256 instead of 512)
3. Ensure sufficient GPU memory

### Permission issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER docker-volumes/
```

## Development

### Rebuilding the image
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Accessing the container
```bash
docker exec -it sadtalker-fastapi bash
```

### Viewing real-time logs
```bash
docker-compose logs -f sadtalker-api
```

## Performance Notes

- **GPU Memory:** Requires ~4-6GB GPU memory for 256px, ~8-12GB for 512px
- **CPU Fallback:** Will use CPU if GPU unavailable (much slower)
- **First Run:** Model download adds ~10-15 minutes to startup
- **Subsequent Runs:** Fast startup (~30-60 seconds)

## File Structure

```
lip-sync-app/
├── Dockerfile                    # Main Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── docker-entrypoint.sh         # Container startup script
├── setup-sad-talker-docker.sh   # SadTalker installation script
├── .dockerignore                # Docker build exclusions
├── DOCKER_README.md             # This file
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
└── docker-volumes/              # Persistent data (created at runtime)
    ├── checkpoints/             # SadTalker models
    ├── gfpgan-weights/          # GFPGAN enhancer models
    ├── uploads/                 # Uploaded files
    ├── results/                 # Generated videos
    └── temp/                    # Temporary files
