from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

app = FastAPI(
    title="Wallet Wealth LLM Advisor", 
    description="AI-powered financial advisory platform", 
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

**Contact Information:**
- Email: sridharan@walletwealth.co.in
- Phone: 9940116967
- Location: Chennai, Tamil Nadu, India

**Services Offered:**
1. Mutual Fund Advisory
2. Portfolio Management
3. Financial Planning
4. Tax Planning
5. Retirement Planning
6. Insurance Planning

**Why Choose Wallet Wealth:**
- SEBI Registered (INA200015440)
- 10+ Years of Experience
- 500+ Happy Clients
- ₹50 Crore+ Assets Under Advisory

**Business Hours:**
Monday to Saturday: 10:00 AM - 6:00 PM
"""

SYSTEM_PROMPT = f"""You are an AI Financial Advisor for Wallet Wealth LLP, a SEBI Registered Investment Advisor based in Chennai, India.

{COMPANY_KNOWLEDGE}

**Your Role:**
1. Provide helpful, accurate financial advice tailored to Indian investors
2. Answer questions about Wallet Wealth LLP using the company information above
3. Recommend suitable investment options based on user's goals and risk profile

**Guidelines:**
- Be professional, friendly, and helpful
- When asked about the CEO, say "Our CEO is S. Sridharan" with his credentials
- When asked about contact, provide phone: 9940116967 and email: sridharan@walletwealth.co.in
- For complex decisions, recommend booking a consultation
- Speak as part of the Wallet Wealth team (use "we", "our", "us")
"""

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise HTTPException(status_code=503, detail="LLM service not configured.")
        from groq import Groq
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


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

appointments_db: list = []


@app.get("/")
async def root():
    return {
        "message": "Welcome to Wallet Wealth LLM Advisor API",
        "version": "1.0.0",
        "status": "running",
        "llm_configured": bool(settings.GROQ_API_KEY)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": bool(settings.GROQ_API_KEY)
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        groq_client = get_groq_client()
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message},
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        return ChatResponse(response=completion.choices[0].message.content, model="llama-3.3-70b-versatile")
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}", model="error")


@app.post("/api/appointments/book")
async def book_appointment(request: AppointmentRequest):
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
    print(f"📅 New Appointment: {request.name} - {request.service_type} on {request.preferred_date}")
    return {
        "id": appointment["id"],
        "message": f"Thank you {request.name}! Your appointment request has been received.",
        "status": "pending"
    }

@app.get("/api/appointments")
async def list_appointments(admin_token: str = None):
    if admin_token != "wallet-wealth-admin-2024":
        raise HTTPException(status_code=401, detail="Admin access required")
    return {"appointments": appointments_db, "total": len(appointments_db)}

@app.get("/api/appointments/stats")
async def appointment_stats(admin_token: str = None):
    if admin_token != "wallet-wealth-admin-2024":
        raise HTTPException(status_code=401, detail="Admin access required")
    pending = len([a for a in appointments_db if a["status"] == "pending"])
    return {"total": len(appointments_db), "pending": pending, "confirmed": 0}