# Task Management REST API - Flask with Prometheus metrics & structured logging
# Endpoints: /health, /metrics, /api/tasks (CRUD) ok 
# Run: gunicorn --bind 0.0.0.0:5000 main:app

import time
import uuid
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify, g
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Initialize Flask app
app = Flask(__name__)

# ===== OBSERVABILITY: Structured Logging =====
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', 'N/A'),
            "module": record.module
        }
        return json.dumps(log_record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# ===== OBSERVABILITY: Prometheus Metrics . =====
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# ===== In-memory Task Storage =====
tasks = {}

# ===== OBSERVABILITY: Request Tracing Middleware =====
@app.before_request
def before_request():
    g.trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
    g.start_time = time.time()
    logger.info(f"Request started: {request.method} {request.path}", 
                extra={'trace_id': g.trace_id})

@app.after_request
def after_request(response):
    latency = time.time() - g.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
    response.headers['X-Trace-ID'] = g.trace_id
    logger.info(f"Request completed: {response.status_code} in {latency:.3f}s",
                extra={'trace_id': g.trace_id})
    return response

# ===== API Endpoints =====
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    return jsonify({"tasks": list(tasks.values()), "count": len(tasks)})

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    task = tasks.get(task_id)
    if not task:
        logger.warning(f"Task not found: {task_id}", extra={'trace_id': g.trace_id})
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    if not data or 'title' not in data:
        logger.error("Invalid request: missing title", extra={'trace_id': g.trace_id})
        return jsonify({"error": "Title is required"}), 400
    
    title = str(data['title']).strip()
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "title": title[:200],  # Limit title length
        "description": str(data.get('description', '')).strip()[:500],
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    tasks[task_id] = task
    logger.info(f"Task created: {task_id}", extra={'trace_id': g.trace_id})
    return jsonify(task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    task = tasks[task_id]
    task['title'] = data.get('title', task['title'])
    task['description'] = data.get('description', task['description'])
    task['completed'] = data.get('completed', task['completed'])
    logger.info(f"Task updated: {task_id}", extra={'trace_id': g.trace_id})
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    del tasks[task_id]
    logger.info(f"Task deleted: {task_id}", extra={'trace_id': g.trace_id})
    return jsonify({"message": "Task deleted successfully"})

if __name__ == '__main__':
    logger.info("Starting Task Management API", extra={'trace_id': 'startup'})
    app.run(host='0.0.0.0', port=5000, debug=False)
