# DevOps Project - Final Report

## Task Management REST API

**Author:** [Your Name]  
**Date:** [Date]  
**Course:** DevOps

---

## 1. Executive Summary

This project demonstrates end-to-end DevOps practices by building a Task Management REST API with complete observability, security scanning, containerization, and Kubernetes deployment. The application is a lightweight Flask-based service (under 150 lines) that provides CRUD operations for task management.

---

## 2. Architecture Overview

### 2.1 Application Architecture

The Task Management API follows a simple monolithic architecture suitable for a microservice:

```
┌────────────────────────────────────────────────────┐
│                    REST API Layer                   │
│  ┌──────────────────────────────────────────────┐ │
│  │  Flask Application (main.py)                  │ │
│  │  ├── /health        (Health Check)           │ │
│  │  ├── /metrics       (Prometheus Metrics)     │ │
│  │  └── /api/tasks     (CRUD Operations)        │ │
│  └──────────────────────────────────────────────┘ │
│                         │                          │
│  ┌──────────────────────────────────────────────┐ │
│  │  Observability Layer                          │ │
│  │  ├── Prometheus Metrics                       │ │
│  │  ├── Structured JSON Logging                  │ │
│  │  └── Request Tracing (X-Trace-ID)            │ │
│  └──────────────────────────────────────────────┘ │
│                         │                          │
│  ┌──────────────────────────────────────────────┐ │
│  │  In-Memory Storage (Dictionary)              │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

### 2.2 Infrastructure Architecture

```
GitHub Repository
       │
       ▼
┌──────────────────┐
│  GitHub Actions  │ ──► Test → SAST → Build → DAST → Deploy
└──────────────────┘
       │
       ▼
┌──────────────────┐
│   Docker Hub     │ ──► Container Image Registry
└──────────────────┘
       │
       ▼
┌──────────────────┐
│   Kubernetes     │ ──► Minikube/Kind Cluster
│   (Minikube)     │
└──────────────────┘
```

---

## 3. Tools and Technologies

| Category | Tool | Purpose |
|----------|------|---------|
| **Language** | Python 3.11 | Backend development |
| **Framework** | Flask | REST API framework |
| **WSGI Server** | Gunicorn | Production server |
| **Metrics** | Prometheus Client | Metrics exposition |
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose | Local development |
| **Kubernetes** | Minikube | Local K8s cluster |
| **CI/CD** | GitHub Actions | Automation pipeline |
| **SAST** | Bandit | Static security scanning |
| **DAST** | OWASP ZAP | Dynamic security scanning |
| **Monitoring** | Prometheus + Grafana | Metrics collection & visualization |

---

## 4. Observability Implementation

### 4.1 Metrics

**Implementation:** Using `prometheus-client` library to expose metrics at `/metrics` endpoint.

**Metrics Collected:**
- `http_requests_total` - Counter for total HTTP requests (labeled by method, endpoint, status)
- `http_request_duration_seconds` - Histogram for request latency

**Sample Output:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/tasks",method="GET",status="200"} 15.0
http_requests_total{endpoint="/api/tasks",method="POST",status="201"} 5.0
```

### 4.2 Structured Logging

**Implementation:** Custom JSON formatter for Python logging.

**Log Fields:**
- `timestamp` - ISO format timestamp
- `level` - Log level (INFO, WARNING, ERROR)
- `message` - Log message
- `trace_id` - Request correlation ID
- `module` - Source module

**Sample Log:**
```json
{"timestamp": "2025-01-15T10:30:00", "level": "INFO", "message": "Task created: abc123", "trace_id": "xyz-789", "module": "main"}
```

### 4.3 Tracing

**Implementation:** Middleware that assigns/propagates `X-Trace-ID` header.

- Auto-generates UUID if not provided
- Propagates through request lifecycle
- Returns in response headers
- Included in all log entries

---

## 5. Security Implementation

### 5.1 SAST (Static Application Security Testing)

**Tool:** Bandit

**Configuration:** Integrated into GitHub Actions pipeline

**Findings:** [Document actual findings here]

### 5.2 DAST (Dynamic Application Security Testing)

**Tool:** OWASP ZAP Baseline Scan

**Configuration:** Runs against deployed container in CI/CD

**Findings:** [Document actual findings here]

### 5.3 Container Security

- **Non-root user:** Application runs as `appuser` (UID 1000)
- **Read-only filesystem:** Container filesystem is read-only
- **No privilege escalation:** `allowPrivilegeEscalation: false`
- **Multi-stage build:** Minimal final image size

---

## 6. Kubernetes Setup

### 6.1 Manifests Created

| Manifest | Purpose |
|----------|---------|
| `namespace.yaml` | Isolated namespace for the application |
| `configmap.yaml` | Environment configuration |
| `deployment.yaml` | Application deployment with 2 replicas |
| `service.yaml` | NodePort service for external access |
| `ingress.yaml` | Ingress for domain-based routing |
| `hpa.yaml` | Horizontal Pod Autoscaler |

### 6.2 Key Features

- **Liveness Probe:** HTTP GET on `/health` every 10s
- **Readiness Probe:** HTTP GET on `/health` every 5s
- **Resource Limits:** 256Mi memory, 500m CPU
- **Auto-scaling:** 2-5 replicas based on CPU/memory

### 6.3 Deployment Commands

```bash
# Start minikube
minikube start

# Build image
eval $(minikube docker-env)
docker build -t task-api:latest .

# Deploy
kubectl apply -f k8s/

# Access
minikube service task-api-service -n task-api --url
```

---

## 7. CI/CD Pipeline

### 7.1 Pipeline Stages

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Test   │ → │  SAST   │ → │  Build  │ → │  DAST   │ → │ Deploy  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 7.2 Stage Details

1. **Test:** Run pytest with coverage
2. **SAST:** Bandit security scan
3. **Build:** Docker image build and push to Docker Hub
4. **DAST:** OWASP ZAP baseline scan
5. **Deploy:** Kubernetes manifest application

### 7.3 Triggers

- Push to `main` or `develop` branches
- Pull requests to `main`

---

## 8. GitHub Workflow

### 8.1 Issues Created

| Issue | Description | Status |
|-------|-------------|--------|
| #1 | Set up Flask REST API | Completed |
| #2 | Add Prometheus metrics | Completed |
| #3 | Implement structured logging | Completed |
| #4 | Create Dockerfile | Completed |
| #5 | Set up CI/CD pipeline | Completed |
| #6 | Add Kubernetes manifests | Completed |
| #7 | Add security scanning | Completed |

### 8.2 Pull Requests

| PR | Description | Reviewer |
|----|-------------|----------|
| #1 | Initial API implementation | [Classmate] |
| #2 | Add observability | [Classmate] |
| #3 | Docker & K8s setup | [Classmate] |

---

## 9. Challenges and Solutions

### Challenge 1: Keeping Code Under 150 Lines
**Solution:** Used Flask's minimal approach, combined metrics and logging into middleware.

### Challenge 2: Container Security
**Solution:** Implemented multi-stage build, non-root user, and read-only filesystem.

### Challenge 3: DAST Integration
**Solution:** Used OWASP ZAP baseline scan with custom rules file to reduce false positives.

---

## 10. Lessons Learned

1. **Observability is Essential:** Having metrics, logs, and tracing from the start makes debugging much easier.

2. **Security Should Be Automated:** Integrating SAST/DAST into CI/CD catches issues early.

3. **Kubernetes Complexity:** Even simple applications require careful resource planning and health checks.

4. **CI/CD Pays Off:** Initial setup time is recovered through automated testing and deployment.

5. **Documentation Matters:** Clear README and inline comments save time for future maintenance.

---

## 11. Future Improvements

- [ ] Add persistent storage (PostgreSQL/Redis)
- [ ] Implement authentication (JWT tokens)
- [ ] Add distributed tracing (Jaeger/Zipkin)
- [ ] Deploy to cloud Kubernetes (EKS/GKE/AKS)
- [ ] Add API rate limiting
- [ ] Implement blue-green deployment

---

## 12. References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OWASP ZAP](https://www.zaproxy.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

---

## Appendix A: API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

---

## Appendix B: Repository Structure

```
devops/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
├── k8s/
├── monitoring/
├── .github/
├── Dockerfile
├── docker-compose.yml
└── README.md
```
