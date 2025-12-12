from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
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

# Initialize Groq client lazily (only when needed)
_groq_client = None


def get_groq_client():
    """Get or create Groq client - lazy initialization"""
    global _groq_client
    
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="LLM service not configured. Please set GROQ_API_KEY environment variable."
            )
        from groq import Groq
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    return _groq_client

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
        "status": "running",
        "llm_configured": bool(settings.GROQ_API_KEY)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": bool(settings.GROQ_API_KEY)
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - sends user message to LLM and returns response
    """
    try:
        # Get Groq client (will raise if not configured)
        groq_client = get_groq_client()
        
        # Call Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful financial advisor assistant for Wallet Wealth LLP. "
                        "Provide clear, accurate financial advice tailored to Indian markets. "
                        "Always remind users to consult with a certified financial advisor for major decisions."
                    ),
                },
                {"role": "user", "content": request.message},
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        response_text = completion.choices[0].message.content

        return ChatResponse(response=response_text, model="llama-3.3-70b-versatile")

    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}", model="error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
