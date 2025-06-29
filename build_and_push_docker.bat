@echo off
echo Building and pushing backend Docker image with GPU support

REM Set variables
set DOCKER_USERNAME=jiufen
set IMAGE_NAME=lypsinc-backend
set TAG=latest

echo.
echo Building Docker image: %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
echo.

REM Build the Docker image
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG% .

echo.
echo Image built successfully!
echo.

REM Login to Docker Hub (you'll be prompted for password)
echo Please login to Docker Hub:
docker login

echo.
echo Pushing image to Docker Hub: %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
echo.

REM Push the image to Docker Hub
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%

echo.
echo Image pushed successfully!
echo.
echo To use this image on RunPod.io:
echo 1. Go to https://www.runpod.io/console/deploy
echo 2. Select "GPU" as the deployment type
echo 3. Enter %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG% as the Docker image
echo 4. Select a GPU template (recommended: at least 8GB VRAM)
echo 5. Make sure to enable "Expose HTTP ports" and set port 8000
echo 6. Configure other settings as needed
echo.
echo Note: This backend image requires GPU support 
echo.

pause
