@echo off
REM Build and deployment script for Insurance Cross-Sell Prediction API (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=insurance-cross-sell-api
set CONTAINER_NAME=insurance-api
set PORT=8000

echo.
echo 🚀 Insurance Cross-Sell Prediction API Build Script
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo.
echo Select build option:
echo 1) Development build (with volume mounts)
echo 2) Production build (optimized)
echo 3) Docker Compose (full stack)
echo 4) Clean up containers and images
set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    echo [INFO] Building development image...
    docker build -t %IMAGE_NAME%:dev -f DockerFile .
    
    echo [INFO] Stopping existing container if running...
    docker stop %CONTAINER_NAME%-dev 2>nul
    docker rm %CONTAINER_NAME%-dev 2>nul
    
    echo [INFO] Running development container...
    docker run -d --name %CONTAINER_NAME%-dev -p %PORT%:8000 -v "%cd%/app:/app/app" -v "%cd%/models:/app/models" %IMAGE_NAME%:dev
    
    echo [INFO] Development container started on port %PORT%
    
) else if "%choice%"=="2" (
    echo [INFO] Building production image...
    docker build -t %IMAGE_NAME%:prod -f Dockerfile.prod .
    
    echo [INFO] Stopping existing container if running...
    docker stop %CONTAINER_NAME%-prod 2>nul
    docker rm %CONTAINER_NAME%-prod 2>nul
    
    echo [INFO] Running production container...
    docker run -d --name %CONTAINER_NAME%-prod -p %PORT%:8000 --restart unless-stopped %IMAGE_NAME%:prod
    
    echo [INFO] Production container started on port %PORT%
    
) else if "%choice%"=="3" (
    echo [INFO] Starting full stack with Docker Compose...
    docker-compose down 2>nul
    docker-compose up --build -d
    
    echo [INFO] Full stack started:
    echo [INFO] - API: http://localhost:8000
    echo [INFO] - MLflow: http://localhost:5000
    
) else if "%choice%"=="4" (
    echo [WARNING] Cleaning up containers and images...
    docker-compose down 2>nul
    docker stop %CONTAINER_NAME%-dev %CONTAINER_NAME%-prod 2>nul
    docker rm %CONTAINER_NAME%-dev %CONTAINER_NAME%-prod 2>nul
    docker rmi %IMAGE_NAME%:dev %IMAGE_NAME%:prod 2>nul
    
    echo [INFO] Cleanup completed
    
) else (
    echo [ERROR] Invalid choice. Please select 1-4.
    exit /b 1
)

REM Health check
if not "%choice%"=="4" (
    echo.
    echo [INFO] Waiting for service to be ready...
    timeout /t 10 /nobreak >nul
    
    curl -f http://localhost:%PORT%/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo [INFO] ✅ Service is healthy and ready!
        echo [INFO] API Documentation: http://localhost:%PORT%/docs
        echo [INFO] Health Check: http://localhost:%PORT%/health
    ) else (
        echo [WARNING] Service might still be starting. Check logs with:
        echo [WARNING] docker logs %CONTAINER_NAME%-dev (or %CONTAINER_NAME%-prod)
    )
)

echo.
echo [INFO] Build script completed successfully! 🎉
pause
