# 🏥 Insurance Health Cross-Sell Prediction - MLOps Project

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-green.svg)](https://fastapi.tiangolo.com)
[![MLflow](https://img.shields.io/badge/MLflow-2.14.3-orange.svg)](https://mlflow.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A comprehensive MLOps pipeline for predicting insurance cross-sell opportunities using machine learning, with production-ready deployment, monitoring, and experiment tracking.**

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📊 Data & Models](#-data--models)
- [🔧 Development Setup](#-development-setup)
- [🐳 Docker Deployment](#-docker-deployment)
- [📈 MLflow Experiment Tracking](#-mlflow-experiment-tracking)
- [📊 Model Monitoring](#-model-monitoring)
- [🔄 CI/CD Pipeline](#-cicd-pipeline)
- [📁 Project Structure](#-project-structure)
- [🛠️ API Documentation](#️-api-documentation)
- [📚 Additional Resources](#-additional-resources)

## 🎯 Project Overview

This project implements an end-to-end MLOps pipeline for predicting whether existing vehicle insurance customers would be interested in health insurance. The solution includes:

### Business Problem

- **Objective**: Predict customer interest in health insurance cross-sell
- **Impact**: Optimize marketing campaigns and improve customer targeting
- **Dataset**: Customer demographics, vehicle details, and insurance history

### Key Features

- ✅ **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- ✅ **Model Versioning**: MLflow model registry with staging/production lifecycle
- ✅ **Production API**: FastAPI with automatic documentation
- ✅ **Data Drift Monitoring**: Evidently AI for model performance tracking
- ✅ **Containerization**: Docker & Docker Compose for consistent deployment
- ✅ **Experiment Tracking**: Complete MLflow integration
- ✅ **Class Imbalance Handling**: SMOTE + Random Under Sampling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  ML Pipeline    │───▶│   Model Store   │
│                 │    │                 │    │    (MLflow)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Validation│    │  Model Training │    │ Model Deployment│
│   & Processing  │    │  & Evaluation   │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Monitoring &    │    │  Experiment     │    │   Production    │
│ Drift Detection │    │   Tracking      │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/your-username/insurance-cross-sell-prediction-mlops-project.git
cd insurance-cross-sell-prediction-mlops-project
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Quick Deploy with Docker

```bash
# Build and run the full stack
docker-compose up --build -d

# Services will be available at:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MLflow: http://localhost:5000
# - Grafana: http://localhost:3000
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "Gender": 1,
       "Age": 44,
       "Driving_License": 1,
       "Region_Code": 28.0,
       "Previously_Insured": 0,
       "Vehicle_Age": 2,
       "Vehicle_Damage": 1,
       "Annual_Premium": 40454.0,
       "Policy_Sales_Channel": 26.0,
       "Vintage": 217,
       "Annual_Premium_log": 10.608196
     }'
```

## 📊 Data & Models

### Dataset Overview

- **Source**: Insurance Cross-Sell Prediction Dataset
- **Size**: ~381K records
- **Features**: 11 input features + 1 target variable
- **Target**: Binary classification (0: Not Interested, 1: Interested)

### Feature Description

| Feature              | Type        | Description                    |
| -------------------- | ----------- | ------------------------------ |
| Gender               | Categorical | Customer gender                |
| Age                  | Numerical   | Customer age                   |
| Driving_License      | Binary      | Driving license status         |
| Region_Code          | Categorical | Customer region code           |
| Previously_Insured   | Binary      | Previously insured status      |
| Vehicle_Age          | Categorical | Age of vehicle                 |
| Vehicle_Damage       | Binary      | Vehicle damage history         |
| Annual_Premium       | Numerical   | Annual premium amount          |
| Policy_Sales_Channel | Categorical | Sales channel                  |
| Vintage              | Numerical   | Customer relationship duration |

### Model Performance

| Model               | Accuracy | ROC-AUC | F1-Score |
| ------------------- | -------- | ------- | -------- |
| **XGBoost**         | 80.76%   | 70.55%  | 83%      |
| Random Forest       | 82.78%   | 64.67%  | 84%      |
| LightGBM            | 82.53%   | 68.43%  | 84%      |
| CatBoost            | 86.26%   | 58.76%  | 85%      |
| Logistic Regression | 64.12%   | 75.83%  | 70%      |

## 🔧 Development Setup

### Training Pipeline

```bash
# Run the training notebook
jupyter notebook Insurance-health-cross-sell-prediction.ipynb

# Or execute training script
python src/train.py
```

### Local Development Server

```bash
# Start FastAPI development server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### MLflow Tracking Server

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

## 🐳 Docker Deployment

### Build Options

#### 1. Development Build

```bash
docker build -t insurance-api:dev -f DockerFile .
docker run -d --name insurance-api-dev -p 8000:8000 insurance-api:dev
```

#### 2. Production Build

```bash
docker build -t insurance-api:prod -f Dockerfile.prod .
docker run -d --name insurance-api-prod -p 8000:8000 --restart unless-stopped insurance-api:prod
```

#### 3. Full Stack (Recommended)

```bash
# Start all services
docker-compose up -d

# Scale API service
docker-compose up --scale insurance-api=3 -d

# View logs
docker-compose logs -f
```

### Build Scripts

```bash
# Linux/macOS
chmod +x build.sh
./build.sh

# Windows
build.bat
```

## 📈 MLflow Experiment Tracking

### Features

- **Experiment Management**: Organized model training runs
- **Model Registry**: Versioned model storage with staging/production lifecycle
- **Metrics Tracking**: Accuracy, ROC-AUC, F1-score, etc.
- **Artifact Storage**: Model files, confusion matrices, reports

### Model Registry Workflow

```python
# Register model
mlflow.register_model(model_uri, "My_Insurance_Model")

# Transition to staging
client.transition_model_version_stage(
    name="My_Insurance_Model",
    version=1,
    stage="Staging"
)

# Promote to production
client.transition_model_version_stage(
    name="My_Insurance_Model",
    version=1,
    stage="Production"
)
```

### MLflow UI Access

- **Local**: http://localhost:5000
- **Docker**: http://localhost:5000 (when using docker-compose)

## 📊 Model Monitoring

### Data Drift Detection with Evidently AI

The project includes comprehensive monitoring using Evidently AI:

```python
# Run monitoring
python evidently_.py
```

### Monitoring Features

- **Data Drift Detection**: Statistical tests for feature drift
- **Model Performance**: Prediction quality monitoring
- **Missing Values**: Data quality checks
- **Batch Processing**: Efficient large dataset monitoring
- **Report Generation**: HTML reports with visualizations
- **Database Integration**: PostgreSQL for metrics storage

### Monitoring Reports

Reports are generated in `app/reports/` directory:

- Batch monitoring reports with timestamps
- Interactive HTML visualizations
- Metrics stored in PostgreSQL database

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (Recommended)

```yaml
name: MLOps Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t insurance-api:${{ github.sha }} .
      - name: Deploy to production
        run: |
          # Add your deployment commands here
```

## 📁 Project Structure

```
insurance-cross-sell-prediction-mlops-project/
│
├── 📊 data/                              # Data files
│   ├── train.csv                         # Training dataset
│   ├── test.csv                          # Test dataset
│   ├── cur_data.csv                      # Current data for monitoring
│   └── ref_data.csv                      # Reference data for monitoring
│
├── 📱 app/                               # Application code
│   ├── main.py                           # FastAPI application
│   ├── predict.py                        # Prediction logic
│   ├── models/                           # Trained models
│   │   ├── My_Insurance_Model_v1/        # Model version 1
│   │   └── My_Insurance_Model_v2/        # Model version 2
│   └── reports/                          # Monitoring reports
│       └── batch_monitoring_report_*.html
│
├── 📈 mlruns/                            # MLflow experiments
├── 📈 mlartifacts/                       # MLflow artifacts
│
├── 🐳 Docker Files
│   ├── DockerFile                        # Development container
│   ├── Dockerfile.prod                   # Production container
│   └── docker-compose.yml               # Multi-service setup
│
├── 🔧 Configuration
│   ├── requirements.txt                  # Python dependencies
│   ├── Procfile                         # Heroku deployment
│   └── .gitignore                       # Git ignore rules
│
├── 📚 Notebooks
│   ├── Insurance-health-cross-sell-prediction.ipynb  # Main training
│   └── data_exploration.ipynb           # EDA notebook
│
├── 📊 Monitoring
│   └── evidently_.py                    # Data drift monitoring
│
├── 🛠️ Scripts
│   ├── build.sh                         # Linux/macOS build script
│   └── build.bat                        # Windows build script
│
└── 📋 Documentation
    ├── README.md                        # Main documentation
    ├── DOCKER_README.md                 # Docker guide
    └── GITHUB_GUIDE.md                  # GitHub best practices
```

## 🛠️ API Documentation

### Endpoints

#### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

#### Prediction

```http
POST /predict
Content-Type: application/json
```

Request body:

```json
{
  "Gender": 1,
  "Age": 44,
  "Driving_License": 1,
  "Region_Code": 28.0,
  "Previously_Insured": 0,
  "Vehicle_Age": 2,
  "Vehicle_Damage": 1,
  "Annual_Premium": 40454.0,
  "Policy_Sales_Channel": 26.0,
  "Vintage": 217,
  "Annual_Premium_log": 10.608196
}
```

Response:

```json
{
  "prediction": [1]
}
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Additional Resources

### Technology Stack

- **🐍 Python 3.9+**: Core programming language
- **⚡ FastAPI**: Modern, fast web framework for APIs
- **🤖 Scikit-learn**: Machine learning library
- **🚀 XGBoost/LightGBM/CatBoost**: Gradient boosting frameworks
- **📊 MLflow**: ML lifecycle management
- **📈 Evidently AI**: ML model monitoring
- **🐳 Docker**: Containerization
- **🔬 Jupyter**: Interactive development
- **📊 Pandas/NumPy**: Data manipulation
- **📈 Matplotlib/Seaborn**: Data visualization

### Dependencies

Key packages and versions:

```
fastapi==0.111.1
mlflow==2.14.3
scikit-learn==1.5.1
pandas==2.2.2
numpy==1.26.4
xgboost
lightgbm
catboost
evidently
imbalanced-learn==0.12.3
uvicorn==0.30.1
```

### Best Practices Implemented

- ✅ **Code Organization**: Modular, maintainable structure
- ✅ **Version Control**: Git with comprehensive .gitignore
- ✅ **Environment Management**: Virtual environments & Docker
- ✅ **Experiment Tracking**: MLflow for reproducibility
- ✅ **Model Versioning**: Semantic versioning in model registry
- ✅ **Data Validation**: Input validation and error handling
- ✅ **Monitoring**: Continuous model performance tracking
- ✅ **Documentation**: Comprehensive docs and API documentation
- ✅ **Testing**: Health checks and validation
- ✅ **Security**: Non-root Docker containers, secret management

### Performance Optimization

- **Class Imbalance**: SMOTE + Random Under Sampling
- **Feature Engineering**: Log transformation, standardization
- **Model Selection**: Cross-validation with multiple algorithms
- **Deployment**: Production-optimized Docker images
- **Monitoring**: Efficient batch processing for large datasets

### Monitoring & Observability

- **Health Checks**: Built-in endpoint monitoring
- **Data Drift**: Automated detection with Evidently AI
- **Model Performance**: Continuous accuracy tracking
- **Logging**: Structured logging throughout the pipeline
- **Metrics Storage**: PostgreSQL integration for historical tracking

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Support

- 📧 **Email**: zinedinerabouh@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Zineddine-Rebbouh/insurance-cross-sell-prediction-mlops-project/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/Zineddine-Rebbouh/insurance-cross-sell-prediction-mlops-project/wiki)

---

**Built with ❤️ for the MLOps Community**

> This project demonstrates production-ready MLOps practices including experiment tracking, model versioning, automated deployment, and continuous monitoring.
