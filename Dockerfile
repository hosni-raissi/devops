# =============================================================================
# DOCKERFILE - Multi-stage Build for Task API
# =============================================================================
# Purpose: Creates a secure, optimized Docker image for the Flask application
# 
# Features:
#   - Multi-stage build: Reduces final image size by separating build/runtime
#   - Non-root user: Runs as 'appuser' for security (prevents container escape)
#   - Health check: Docker monitors container health via /health endpoint
#   - Gunicorn: Production-grade WSGI server (not Flask's dev server)
#
# Build: docker build -t task-api .
# Run:   docker run -p 5000:5000 task-api
# =============================================================================

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /tmp && chmod 1777 /tmp

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/main.py .

# Ensure proper ownership
RUN chown -R appuser:appuser /app

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "main:app"]
