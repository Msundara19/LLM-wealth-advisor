import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Mock the settings and Groq before importing the app
mock_settings = Mock()
mock_settings.GROQ_API_KEY = "test-key"
mock_settings.LLM_PROVIDER = "groq"
mock_settings.LLM_TEMPERATURE = 0.7
mock_settings.LLM_MAX_TOKENS = 1024

@pytest.fixture
def client():
    """Create a test client with mocked dependencies"""
    with patch('app.main_minimal.settings', mock_settings), \
         patch('app.main_minimal.Groq') as mock_groq:
        # Setup the mock response
        mock_groq_instance = MagicMock()
        mock_groq.return_value = mock_groq_instance
        
        from app.main_minimal import app
        
        # Store the mock for use in tests
        app.state.mock_groq = mock_groq_instance
        
        yield TestClient(app)

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

def test_chat_endpoint_success(client):
    """Test chat endpoint with successful response"""
    # Mock the Groq API response
    mock_completion = Mock()
    mock_completion.choices = [Mock()]
    mock_completion.choices[0].message.content = "This is a test financial advice"
    
    # Access the mock through app state
    from app.main_minimal import groq_client
    with patch.object(groq_client.chat.completions, 'create', return_value=mock_completion):
        response = client.post("/api/chat", json={"message": "How should I invest?"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "This is a test financial advice"
        assert data["model"] == "llama-3.3-70b-versatile"

def test_chat_endpoint_error_handling(client):
    """Test chat endpoint error handling"""
    from app.main_minimal import groq_client
    
    # Mock an error from Groq
    with patch.object(groq_client.chat.completions, 'create', side_effect=Exception("API Error")):
        response = client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert "Error" in data["response"]
        assert data["model"] == "error"

def test_api_docs_accessible(client):
    """Test that API docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
