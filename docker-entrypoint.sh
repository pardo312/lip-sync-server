#!/bin/bash
set -e

echo "Starting SadTalker FastAPI application..."

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate sadtalker

# Function to download models if they don't exist
download_models() {
    echo "Checking for SadTalker models..."
    
    cd /app/SadTalker
    
    # Check if main models exist
    models_exist=true
    if [ ! -f "./checkpoints/mapping_00109-model.pth.tar" ] || \
       [ ! -f "./checkpoints/mapping_00229-model.pth.tar" ] || \
       [ ! -f "./checkpoints/SadTalker_V0.0.2_256.safetensors" ] || \
       [ ! -f "./checkpoints/SadTalker_V0.0.2_512.safetensors" ]; then
        models_exist=false
    fi
    
    # Check if GFPGAN enhancer models exist
    enhancer_exist=true
    if [ ! -f "./gfpgan/weights/alignment_WFLW_4HG.pth" ] || \
       [ ! -f "./gfpgan/weights/detection_Resnet50_Final.pth" ] || \
       [ ! -f "./gfpgan/weights/GFPGANv1.4.pth" ] || \
       [ ! -f "./gfpgan/weights/parsing_parsenet.pth" ]; then
        enhancer_exist=false
    fi
    
    if [ "$models_exist" = false ] || [ "$enhancer_exist" = false ]; then
        echo "Models not found. Downloading models using official script..."
        echo "This may take several minutes depending on your internet connection..."
        
        # Make the download script executable and run it
        chmod +x scripts/download_models.sh
        bash scripts/download_models.sh
        
        echo "Model download completed!"
    else
        echo "All models found. Skipping download."
    fi
    
    cd /app
}

# Download models if needed
download_models

# Start the FastAPI application
echo "Starting FastAPI server..."
cd /app
python main.py
