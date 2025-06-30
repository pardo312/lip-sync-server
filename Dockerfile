FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04

# Set working directory to your app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.8 python3.8-dev python3.8-distutils python3-pip \
    git wget curl ffmpeg \
    libsm6 libxext6 libxrender-dev libglib2.0-0 \
    libgl1-mesa-glx libgtk-3-0 \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libatlas-base-dev gfortran build-essential cmake pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.8 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# Install pip for Python 3.8
RUN curl https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8

# Upgrade pip and basic tools
RUN python3.8 -m pip install --upgrade pip setuptools wheel

# Clone SadTalker into container
RUN git clone https://github.com/OpenTalker/SadTalker.git /app/SadTalker

# Add SadTalker to Python path and set SadTalker path
ENV PYTHONPATH="/app/SadTalker:${PYTHONPATH}"
ENV SADTALKER_PATH="/app/SadTalker"

# Install SadTalker requirements
RUN pip install -r /app/SadTalker/requirements.txt

# Install PyTorch with CUDA 12.1 support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Uninstall and reinstall critical packages
RUN pip uninstall basicsr gfpgan -y && \
    pip install git+https://github.com/xinntao/BasicSR.git && \
    pip install git+https://github.com/TencentARC/GFPGAN.git

# Additional packages
RUN pip install opencv-python facexlib

# Copy your app files
COPY . .

# Install your own app dependencies
RUN pip install -r requirements.txt

# Ensure start.sh is executable
RUN chmod +x start.sh

# Create necessary runtime folders
RUN mkdir -p /uploads /results /temp

EXPOSE 8000

CMD ["./start.sh"]
