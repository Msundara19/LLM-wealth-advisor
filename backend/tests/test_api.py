import pytest
import os
from unittest.mock import Mock, patch

# CRITICAL: Set fake API key BEFORE any imports that use it
os.environ.setdefault('GROQ_API_KEY', 'test-fake-key-for-testing')

from fastapi.testclient import TestClient

@pytest.fixture
def mock_groq():
    """Mock Groq client completions"""
    with patch('app.main_minimal.groq_client.chat.completions.create') as mock:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response from AI"
        mock.return_value = mock_response
        yield mock

@pytest.fixture
def client():
    """Create test client"""
    from app.main_minimal import app
    return TestClient(app)

def test_read_root(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Wallet Wealth LLM Advisor API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data

def test_chat_endpoint_success(client, mock_groq):
    """Test chat endpoint with mocked Groq response"""
    mock_groq.return_value.choices[0].message.content = "Great investment advice here"
    
    response = client.post("/api/chat", json={"message": "How should I invest?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["model"] == "llama-3.3-70b-versatile"
    assert mock_groq.called

def test_chat_endpoint_error_handling(client, mock_groq):
    """Test chat endpoint error handling"""
    mock_groq.side_effect = Exception("API Error")
    
    response = client.post("/api/chat", json={"message": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert "Error" in data["response"]
    assert data["model"] == "error"

def test_api_docs_accessible(client):
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
