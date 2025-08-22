#!/bin/bash

# Build and deployment script for Insurance Cross-Sell Prediction API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="insurance-cross-sell-api"
CONTAINER_NAME="insurance-api"
PORT=8000

echo -e "${GREEN}🚀 Insurance Cross-Sell Prediction API Build Script${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build options
echo "Select build option:"
echo "1) Development build (with volume mounts)"
echo "2) Production build (optimized)"
echo "3) Docker Compose (full stack)"
echo "4) Clean up containers and images"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_status "Building development image..."
        docker build -t ${IMAGE_NAME}:dev -f DockerFile .
        
        print_status "Stopping existing container if running..."
        docker stop ${CONTAINER_NAME}-dev 2>/dev/null || true
        docker rm ${CONTAINER_NAME}-dev 2>/dev/null || true
        
        print_status "Running development container..."
        docker run -d \
            --name ${CONTAINER_NAME}-dev \
            -p ${PORT}:8000 \
            -v "$(pwd)/app:/app/app" \
            -v "$(pwd)/models:/app/models" \
            ${IMAGE_NAME}:dev
        
        print_status "Development container started on port ${PORT}"
        ;;
        
    2)
        print_status "Building production image..."
        docker build -t ${IMAGE_NAME}:prod -f Dockerfile.prod .
        
        print_status "Stopping existing container if running..."
        docker stop ${CONTAINER_NAME}-prod 2>/dev/null || true
        docker rm ${CONTAINER_NAME}-prod 2>/dev/null || true
        
        print_status "Running production container..."
        docker run -d \
            --name ${CONTAINER_NAME}-prod \
            -p ${PORT}:8000 \
            --restart unless-stopped \
            ${IMAGE_NAME}:prod
        
        print_status "Production container started on port ${PORT}"
        ;;
        
    3)
        print_status "Starting full stack with Docker Compose..."
        docker-compose down 2>/dev/null || true
        docker-compose up --build -d
        
        print_status "Full stack started:"
        print_status "- API: http://localhost:8000"
        print_status "- MLflow: http://localhost:5000"
        ;;
        
    4)
        print_warning "Cleaning up containers and images..."
        docker-compose down 2>/dev/null || true
        docker stop ${CONTAINER_NAME}-dev ${CONTAINER_NAME}-prod 2>/dev/null || true
        docker rm ${CONTAINER_NAME}-dev ${CONTAINER_NAME}-prod 2>/dev/null || true
        docker rmi ${IMAGE_NAME}:dev ${IMAGE_NAME}:prod 2>/dev/null || true
        
        print_status "Cleanup completed"
        ;;
        
    *)
        print_error "Invalid choice. Please select 1-4."
        exit 1
        ;;
esac

# Health check
if [ "$choice" != "4" ]; then
    echo ""
    print_status "Waiting for service to be ready..."
    sleep 10
    
    if curl -f http://localhost:${PORT}/health > /dev/null 2>&1; then
        print_status "✅ Service is healthy and ready!"
        print_status "API Documentation: http://localhost:${PORT}/docs"
        print_status "Health Check: http://localhost:${PORT}/health"
    else
        print_warning "Service might still be starting. Check logs with:"
        print_warning "docker logs ${CONTAINER_NAME}-dev (or ${CONTAINER_NAME}-prod)"
    fi
fi

echo ""
print_status "Build script completed successfully! 🎉"
