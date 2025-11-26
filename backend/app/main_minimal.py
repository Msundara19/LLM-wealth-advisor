
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Wallet Wealth LLM Advisor",
    description="AI-powered financial advisory platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    response: str
    model: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Wallet Wealth LLM Advisor API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "llm_provider": settings.LLM_PROVIDER}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - sends user message to LLM and returns response
    """
    try:
        # Call Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful financial advisor assistant. Provide clear, accurate financial advice."
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        
        response_text = completion.choices[0].message.content
        
        return ChatResponse(
            response=response_text,
            model="llama-3.3-70b-versatile"
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            model="error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)