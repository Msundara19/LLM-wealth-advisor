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

# Wallet Wealth Company Knowledge Base
COMPANY_KNOWLEDGE = """
=== WALLET WEALTH LLP - COMPANY INFORMATION ===

**Company Overview:**
- Name: Wallet Wealth LLP
- Tagline: "The Winners Choice"
- Type: SEBI Registered Investment Advisor
- SEBI Registration Number: INA200015440
- Website: https://www.walletwealth.co.in

**Leadership:**
- CEO & Principal Officer: S. Sridharan
  - Over two decades of experience in financial planning and wealth management
  - Has helped thousands of individuals achieve their financial goals
  - Holds Associate Financial Planner certification for Retirement Planning and Employee Benefits from the Financial Planning Standards Board
  - Previously worked with leading financial advisory firms: FundsIndia, Quantum, and Allegro Capital
  - Expertise: Investment advisory, retirement planning, client-centric financial solutions
  - A recognised voice in personal finance ecosystem, contributes to top financial platforms and publications

**Contact Information:**
- Email: sridharan@walletwealth.co.in
- Phone: 9940116967
- Location: Chennai, Tamil Nadu, India

**Services Offered:**
1. Mutual Fund Advisory - Expert fund selection and SIP planning
2. Portfolio Management - Comprehensive wealth management
3. Financial Planning - Goal-based investment strategies
4. Tax Planning - Optimize tax savings through 80C, 80D investments
5. Retirement Planning - Secure your future with proper planning
6. Insurance Planning - Life and health insurance advisory

**Why Choose Wallet Wealth:**
- SEBI Registered - Fully compliant and regulated
- 10+ Years of Experience
- 500+ Happy Clients
- ₹50 Crore+ Assets Under Advisory
- Personalized Approach - Tailored advice for each client
- Transparent Fee Structure - No hidden charges

**Business Hours:**
Monday to Saturday: 10:00 AM - 6:00 PM

=== END OF COMPANY INFORMATION ===
"""

SYSTEM_PROMPT = f"""You are an AI Financial Advisor for Wallet Wealth LLP, a SEBI Registered Investment Advisor based in Chennai, India.

{COMPANY_KNOWLEDGE}

**Your Role:**
1. Provide helpful, accurate financial advice tailored to Indian investors
2. Answer questions about Wallet Wealth LLP using the company information above
3. Recommend suitable investment options based on user's goals and risk profile
4. Explain complex financial concepts in simple terms
5. Always mention SEBI registration when discussing credibility
6. Encourage users to book appointments for personalized advice

**Guidelines:**
- Be professional, friendly, and helpful
- When asked about the CEO or leadership, mention S. Sridharan with his credentials
- When asked about contact, provide the phone number and email
- For complex financial decisions, recommend booking a consultation
- Always remind users that past performance doesn't guarantee future returns
- Mention that mutual fund investments are subject to market risks

**Important:** You represent Wallet Wealth LLP. Always speak as if you are part of the team.
Instead of saying "Wallet Wealth's CEO is...", say "Our CEO is S. Sridharan..."
"""

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


class AppointmentRequest(BaseModel):
    name: str
    email: str
    phone: str
    service_type: str
    preferred_date: str
    preferred_time: str
    message: Optional[str] = None


# In-memory storage for appointments (for demo/minimal mode)
appointments_db: list = []


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
                    "content": SYSTEM_PROMPT,
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


# Appointment endpoints
@app.post("/api/appointments/book")
async def book_appointment(request: AppointmentRequest):
    """
    Book a new appointment
    """
    appointment = {
        "id": len(appointments_db) + 1,
        "name": request.name,
        "email": request.email,
        "phone": request.phone,
        "service_type": request.service_type,
        "preferred_date": request.preferred_date,
        "preferred_time": request.preferred_time,
        "message": request.message,
        "status": "pending",
        "created_at": __import__('datetime').datetime.now().isoformat()
    }
    
    appointments_db.append(appointment)
    
    print(f"📅 New Appointment: {request.name} - {request.service_type} on {request.preferred_date} at {request.preferred_time}")
    print(f"   Contact: {request.phone} | {request.email}")
    
    return {
        "id": appointment["id"],
        "message": f"Thank you {request.name}! Your appointment request has been received. We will contact you at {request.phone} to confirm.",
        "status": "pending"
    }


@app.get("/api/appointments")
async def list_appointments(admin_token: str = None):
    """
    List all appointments (simple admin auth)
    """
    if admin_token != "wallet-wealth-admin-2024":
        raise HTTPException(status_code=401, detail="Admin access required. Add ?admin_token=wallet-wealth-admin-2024")
    
    return {
        "appointments": appointments_db,
        "total": len(appointments_db)
    }


@app.get("/api/appointments/stats")
async def appointment_stats(admin_token: str = None):
    """
    Get appointment statistics
    """
    if admin_token != "wallet-wealth-admin-2024":
        raise HTTPException(status_code=401, detail="Admin access required")
    
    pending = len([a for a in appointments_db if a["status"] == "pending"])
    confirmed = len([a for a in appointments_db if a["status"] == "confirmed"])
    
    return {
        "total": len(appointments_db),
        "pending": pending,
        "confirmed": confirmed
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)