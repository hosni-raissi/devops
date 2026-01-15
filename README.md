# Task Management API - DevOps Project

A small REST API for task management, built with Flask and designed to demonstrate DevOps best practices including containerization, CI/CD, observability, and security scanning.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Docker Usage](#docker-usage)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Documentation](#api-documentation)
- [Observability](#observability)
- [Security](#security)
- [CI/CD Pipeline](#cicd-pipeline)

## 🎯 Overview

This project implements a Task Management REST API (under 150 lines) with:
- Full CRUD operations for tasks
- Prometheus metrics endpoint
- Structured JSON logging
- Request tracing with trace IDs
- Health check endpoint for Kubernetes probes

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   Test   │→ │   SAST   │→ │  Build   │→ │   DAST   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   task-api Namespace                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod N   │  (HPA)   │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  │         ↓            ↓            ↓                  │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │              Service (NodePort)               │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Observability                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Prometheus  │→ │   Grafana    │  │  Structured  │      │
│  │   Metrics    │  │  Dashboard   │  │    Logs      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **REST API** | Full CRUD for task management |
| **Metrics** | Prometheus metrics (request count, latency) |
| **Logging** | Structured JSON logs with trace IDs |
| **Tracing** | Request tracing via X-Trace-ID headers |
| **Health Checks** | Kubernetes-ready liveness/readiness probes |
| **Security** | SAST (Bandit) + DAST (OWASP ZAP) scanning |
| **Container** | Multi-stage Docker build, non-root user |
| **Kubernetes** | Full manifests with HPA auto-scaling |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- kubectl & minikube (for Kubernetes deployment)

### Clone and Run

```bash
# Clone the repository
git clone https://github.com/yourusername/task-api.git
cd task-api

# Run with Docker Compose
docker-compose up -d

# Access the API
curl http://localhost:5000/health
```

## 💻 Local Development

### Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r app/requirements.txt

# Run the application
cd app
python main.py
```

### Run Tests

```bash
cd app
pytest tests/ -v --cov=. --cov-report=html
```

## 🐳 Docker Usage

### Build Image

```bash
docker build -t task-api:latest .
```

### Run Container

```bash
docker run -d -p 5000:5000 --name task-api task-api:latest
```

### Docker Compose (Full Stack)

```bash
# Start all services (API + Prometheus + Grafana)
docker-compose up -d

# View logs
docker-compose logs -f task-api

# Stop services
docker-compose down
```

**Services:**
- API: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

## ☸️ Kubernetes Deployment

### Minikube Setup

```bash
# Start minikube
minikube start

# Build image in minikube's Docker
eval $(minikube docker-env)
docker build -t task-api:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Get service URL
minikube service task-api-service -n task-api --url
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n task-api

# Check service
kubectl get svc -n task-api

# View logs
kubectl logs -l app=task-api -n task-api -f
```

## 📡 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| POST | `/api/tasks` | Create new task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

### Examples

```bash
# Health check
curl http://localhost:5000/health

# Create a task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn DevOps", "description": "Complete the project"}'

# List all tasks
curl http://localhost:5000/api/tasks

# Get specific task
curl http://localhost:5000/api/tasks/{task_id}

# Update a task
curl -X PUT http://localhost:5000/api/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a task
curl -X DELETE http://localhost:5000/api/tasks/{task_id}
```

## 📊 Observability

### Metrics

Access Prometheus metrics at `/metrics`:

```bash
curl http://localhost:5000/metrics
```

**Available Metrics:**
- `http_requests_total` - Total HTTP requests (by method, endpoint, status)
- `http_request_duration_seconds` - Request latency histogram

### Logs

Structured JSON logs include:
- Timestamp
- Log level
- Message
- Trace ID
- Module

**Sample Log:**
```json
{
  "timestamp": "2025-01-15T10:30:00.000000",
  "level": "INFO",
  "message": "Request started: POST /api/tasks",
  "trace_id": "abc-123-def",
  "module": "main"
}
```

### Tracing

Every request receives a unique `X-Trace-ID` header for correlation:

```bash
# Request with custom trace ID
curl -H "X-Trace-ID: my-trace-123" http://localhost:5000/api/tasks

# Response includes X-Trace-ID header
```

## 🔒 Security

### SAST (Static Analysis)

Using **Bandit** for Python security scanning:

```bash
pip install bandit
bandit -r app/ -f txt
```

### DAST (Dynamic Analysis)

Using **OWASP ZAP** for runtime security scanning:

```bash
# Run ZAP against deployed API
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://host.docker.internal:5000
```

### Security Features

- Non-root container user
- Read-only filesystem
- No privilege escalation
- Multi-stage Docker build (minimal attack surface)

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline includes:

1. **Test** - Run pytest with coverage
2. **SAST** - Bandit security scan
3. **Build** - Docker image build & push
4. **DAST** - OWASP ZAP baseline scan
5. **Deploy** - Kubernetes deployment

### Required Secrets

Configure these in GitHub repository settings:
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password/token

## 📁 Project Structure

```
devops/
├── app/
│   ├── main.py              # Flask API (under 150 lines)
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       └── test_main.py     # Unit tests
├── k8s/
│   ├── namespace.yaml       # Kubernetes namespace
│   ├── configmap.yaml       # Configuration
│   ├── deployment.yaml      # Deployment with probes
│   ├── service.yaml         # NodePort service
│   ├── ingress.yaml         # Ingress (optional)
│   └── hpa.yaml             # Horizontal Pod Autoscaler
├── monitoring/
│   ├── prometheus.yml       # Prometheus config
│   └── grafana/
│       └── provisioning/
│           └── datasources/ # Grafana datasources
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions pipeline
├── .zap/
│   └── rules.tsv            # ZAP scan rules
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Local development stack
├── .dockerignore            # Docker ignore file
└── README.md                # This file
```

## 📝 License

MIT License - feel free to use for educational purposes.

## 👤 Author

Your Name - DevOps Course Project
