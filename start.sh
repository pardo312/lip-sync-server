#!/bin/bash

# Startup script for SadTalker API
# This script downloads models if they don't exist, then starts the FastAPI application

set -e

echo "Starting SadTalker API..."

# Change to SadTalker directory for model downloads
cd /app/SadTalker

# Check if models exist, if not download them
if [ ! -f "./checkpoints/SadTalker_V0.0.2_256.safetensors" ] || [ ! -f "./checkpoints/SadTalker_V0.0.2_512.safetensors" ]; then
    echo "Models not found. Downloading SadTalker models..."
    
    # Make sure checkpoints directory exists
    mkdir -p ./checkpoints
    mkdir -p ./gfpgan/weights
    
    # Download main SadTalker models
    echo "Downloading mapping models..."
    wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar -O ./checkpoints/mapping_00109-model.pth.tar
    wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar -O ./checkpoints/mapping_00229-model.pth.tar
    
    echo "Downloading SadTalker models..."
    wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors -O ./checkpoints/SadTalker_V0.0.2_256.safetensors
    wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors -O ./checkpoints/SadTalker_V0.0.2_512.safetensors
    
    echo "Downloading GFPGAN enhancer models..."
    wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth -O ./gfpgan/weights/alignment_WFLW_4HG.pth 
    wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth -O ./gfpgan/weights/detection_Resnet50_Final.pth 
    wget -nc https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -O ./gfpgan/weights/GFPGANv1.4.pth 
    wget -nc https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth -O ./gfpgan/weights/parsing_parsenet.pth
    
    echo "Model download completed!"
else
    echo "Models already exist, skipping download."
fi

# Change back to app directory
cd /app

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info --access-log

