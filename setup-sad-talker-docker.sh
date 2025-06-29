#!/bin/bash
set -e

echo "Setting up SadTalker for Docker environment..."

# Clone SadTalker repository
if [ ! -d "SadTalker" ]; then
    echo "Cloning SadTalker repository..."
    git clone https://github.com/OpenTalker/SadTalker.git
fi

cd SadTalker

echo "Installing Python dependencies..."

# Install requirements using conda run to ensure we're in the right environment
conda run -n sadtalker pip install -r requirements.txt

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
conda run -n sadtalker pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Check PyTorch installation
echo "Checking PyTorch installation..."
conda run -n sadtalker python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

# Uninstall and reinstall specific packages for compatibility
echo "Setting up compatible versions of basicsr and gfpgan..."
conda run -n sadtalker pip uninstall basicsr gfpgan -y
conda run -n sadtalker pip install git+https://github.com/xinntao/BasicSR.git
conda run -n sadtalker pip install git+https://github.com/TencentARC/GFPGAN.git

# Install additional dependencies
echo "Installing additional dependencies..."
conda run -n sadtalker pip install opencv-python facexlib

echo "SadTalker setup completed successfully!"
echo "Note: Models will be downloaded automatically on first use."

cd ..
