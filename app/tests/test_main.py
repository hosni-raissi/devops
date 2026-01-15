"""
Unit tests for Task Management API
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, tasks


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        tasks.clear()
        yield client


def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'http_requests_total' in response.data


def test_get_empty_tasks(client):
    """Test getting tasks when empty"""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 0
    assert data['tasks'] == []


def test_create_task(client):
    """Test creating a task"""
    response = client.post('/api/tasks', 
                          json={'title': 'Test Task', 'description': 'Test Description'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'Test Description'
    assert data['completed'] == False
    assert 'id' in data


def test_create_task_missing_title(client):
    """Test creating a task without title"""
    response = client.post('/api/tasks', json={'description': 'No title'})
    assert response.status_code == 400


def test_get_task(client):
    """Test getting a specific task"""
    # Create a task first
    create_response = client.post('/api/tasks', json={'title': 'Get Test'})
    task_id = create_response.get_json()['id']
    
    # Get the task
    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Get Test'


def test_get_task_not_found(client):
    """Test getting non-existent task"""
    response = client.get('/api/tasks/nonexistent')
    assert response.status_code == 404


def test_update_task(client):
    """Test updating a task"""
    # Create a task
    create_response = client.post('/api/tasks', json={'title': 'Original'})
    task_id = create_response.get_json()['id']
    
    # Update it
    response = client.put(f'/api/tasks/{task_id}', 
                         json={'title': 'Updated', 'completed': True})
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated'
    assert data['completed'] == True


def test_delete_task(client):
    """Test deleting a task"""
    # Create a task
    create_response = client.post('/api/tasks', json={'title': 'To Delete'})
    task_id = create_response.get_json()['id']
    
    # Delete it
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    """Test deleting non-existent task"""
    response = client.delete('/api/tasks/nonexistent')
    assert response.status_code == 404
