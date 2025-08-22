# Docker Deployment Guide

This guide explains how to build and deploy the Insurance Cross-Sell Prediction API using Docker.

## 🐳 Docker Files Overview

- **`DockerFile`**: Development-optimized container
- **`Dockerfile.prod`**: Production-optimized multi-stage build
- **`docker-compose.yml`**: Full stack deployment with MLflow
- **`build.sh`** / **`build.bat`**: Automated build scripts

## 🚀 Quick Start

### Option 1: Using Build Scripts (Recommended)

**Linux/macOS:**

```bash
chmod +x build.sh
./build.sh
```

**Windows:**

```cmd
build.bat
```

### Option 2: Manual Docker Commands

**Development Build:**

```bash
# Build the image
docker build -t insurance-api:dev -f DockerFile .

# Run the container
docker run -d --name insurance-api-dev -p 8000:8000 insurance-api:dev
```

**Production Build:**

```bash
# Build the optimized image
docker build -t insurance-api:prod -f Dockerfile.prod .

# Run the container
docker run -d --name insurance-api-prod -p 8000:8000 --restart unless-stopped insurance-api:prod
```

**Full Stack with Docker Compose:**

```bash
docker-compose up --build -d
```

## 📊 Services

After deployment, the following services will be available:

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MLflow UI** (if using docker-compose): http://localhost:5000

## 🔧 Configuration

### Environment Variables

| Variable      | Default | Description                |
| ------------- | ------- | -------------------------- |
| `PORT`        | 8000    | API server port            |
| `WORKERS`     | 1       | Number of worker processes |
| `MAX_WORKERS` | 4       | Maximum worker processes   |
| `PYTHONPATH`  | /app    | Python path                |

### Docker Compose Configuration

Customize `docker-compose.yml` for your environment:

```yaml
services:
  insurance-api:
    environment:
      - PORT=8080 # Change port
      - WORKERS=2 # Increase workers
    ports:
      - "8080:8080" # Update port mapping
```

## 🏥 Health Monitoring

The containers include built-in health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' insurance-api-prod
```

## 📝 Logs

View application logs:

```bash
# Development container
docker logs insurance-api-dev -f

# Production container
docker logs insurance-api-prod -f

# Docker Compose
docker-compose logs -f insurance-api
```

## 🔄 Updates and Maintenance

### Updating the Application

1. **Development**: Volume mounts enable hot reloading
2. **Production**: Rebuild and redeploy the container

```bash
# Stop and remove old container
docker stop insurance-api-prod
docker rm insurance-api-prod

# Build new image
docker build -t insurance-api:prod -f Dockerfile.prod .

# Run updated container
docker run -d --name insurance-api-prod -p 8000:8000 --restart unless-stopped insurance-api:prod
```

### Updating Models

For production, models are baked into the container. To update:

1. Replace model files in the `models/` directory
2. Rebuild the container
3. Deploy the new version

For development, models are mounted as volumes and can be updated without rebuilding.

## 🛡️ Security Features

- **Non-root user**: Containers run as `appuser`
- **Minimal base image**: Uses `python:3.9-slim`
- **Multi-stage build**: Production images exclude build dependencies
- **Health checks**: Built-in monitoring
- **Resource limits**: Configurable via Docker

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**:

   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000

   # Use a different port
   docker run -p 8001:8000 insurance-api:prod
   ```

2. **Models not found**:

   - Ensure `models/` directory exists
   - Check file permissions
   - Verify model files are not in `.dockerignore`

3. **Memory issues**:
   ```bash
   # Increase container memory
   docker run -m 2g insurance-api:prod
   ```

### Debug Mode

Run containers in debug mode:

```bash
# Interactive mode
docker run -it --rm insurance-api:dev /bin/bash

# Override command
docker run -it insurance-api:dev python app/main.py
```

## 📊 Performance Optimization

### Production Recommendations

1. **Use multi-stage builds** (Dockerfile.prod)
2. **Set appropriate worker count** based on CPU cores
3. **Configure resource limits**:
   ```bash
   docker run --cpus="2" -m="2g" insurance-api:prod
   ```
4. **Use external model storage** for large models
5. **Implement caching** for frequently accessed data

### Monitoring

Consider adding monitoring tools:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation
- **Jaeger**: Distributed tracing

## 🔗 Integration

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Build and Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t insurance-api:${{ github.sha }} -f Dockerfile.prod .
      - name: Deploy to production
        run: |
          docker stop insurance-api-prod || true
          docker rm insurance-api-prod || true
          docker run -d --name insurance-api-prod -p 8000:8000 insurance-api:${{ github.sha }}
```

### Cloud Deployment

The containers are ready for deployment to:

- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Kubernetes**

Example Kubernetes deployment available in `k8s/` directory (if needed).

---

For additional support, check the application logs or open an issue in the repository.
