# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh && \
    conda clean -tipsy

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Create conda environment and install dependencies
RUN conda create -n sadtalker python=3.8 -y && \
    echo "source activate sadtalker" > ~/.bashrc

# Install conda packages in the sadtalker environment
RUN conda run -n sadtalker conda install ffmpeg -y

# Copy and run the Docker-optimized setup script
COPY setup-sad-talker-docker.sh /app/
RUN chmod +x setup-sad-talker-docker.sh && \
    bash setup-sad-talker-docker.sh

# Install FastAPI application dependencies
RUN conda run -n sadtalker pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads /app/results /app/temp /app/SadTalker/checkpoints

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Copy startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
