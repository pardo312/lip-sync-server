# Use NVIDIA CUDA base image with cuDNN support
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.8 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# Install pip for Python 3.8
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.8

# Upgrade pip and install basic Python packages
RUN python3.8 -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Clone SadTalker repository
RUN git clone https://github.com/OpenTalker/SadTalker.git

# Set working directory to SadTalker
WORKDIR /app/SadTalker

# Install SadTalker requirements
RUN pip install -r requirements.txt

# Install PyTorch with CUDA 12.1 support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Uninstall conflicting packages and install updated versions
RUN pip uninstall basicsr gfpgan -y
RUN pip install git+https://github.com/xinntao/BasicSR.git
RUN pip install git+https://github.com/TencentARC/GFPGAN.git

# Install additional required packages
RUN pip install opencv-python facexlib

# Copy your application code directly to /app
WORKDIR /app
COPY . .

# Install your application requirements
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads \
    /app/results \
    /app/temp

# Make startup script executable
RUN chmod +x /app/start.sh

# Set up Python path to include SadTalker modules
ENV PYTHONPATH="/app/SadTalker:/app:$PYTHONPATH"

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Set working directory to your application
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Command to run startup script
CMD ["./start.sh"]
