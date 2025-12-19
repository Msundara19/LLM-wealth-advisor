# LLM Wealth Advisor for Wallet Wealth
<img width="1142" height="845" alt="image" src="https://github.com/user-attachments/assets/fd4d9162-fadb-4b38-b51b-8c697c5c987c" />

<img width="1130" height="848" alt="image" src="https://github.com/user-attachments/assets/5e682d24-055b-40ce-9ab9-32e38c69980e" />


click here to view the application : https://llm-wealth-advisor.vercel.app/
A sophisticated AI-powered financial advisor chatbot integrated into Wallet Wealth's website, providing personalized investment guidance, portfolio analysis, and financial planning assistance.

## Features

- 🤖 AI-powered financial advisory using Groq/Llama 3.3 70B
- 💼 Portfolio analysis and recommendations
- 📊 Real-time financial guidance for Indian markets
- 🔒 Secure authentication and admin dashboard
- 📱 Responsive web interface
- 🚀 Production-ready Vercel deployment
- 📅 Appointment booking system with email notifications

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Groq API** - LLM inference with Llama 3.3 70B
- **Vercel Serverless** - API functions deployment
- **Python 3.12** - Runtime environment

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing

### Infrastructure
- **Vercel** - Full-stack deployment
- **GitHub Actions** - CI/CD pipeline
- **EmailJS** - Email notification service

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key ([console.groq.com](https://console.groq.com))
- Git

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Msundara19/LLM-wealth-advisor.git
cd LLM-wealth-advisor
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export GROQ_API_KEY=your_groq_key
uvicorn app.main_minimal:app --reload --port 8000
```

4. Start Frontend:
```bash
cd frontend
npm install
npm start
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
LLM-wealth-advisor/
├── api/                          # Vercel Serverless Functions
│   ├── chat.py                   # AI chat endpoint
│   ├── appointments.py           # Booking endpoint
│   └── index.py                  # Health check
├── backend/
│   ├── app/
│   │   ├── api/                  # API routes
│   │   ├── core/                 # Config, database, security
│   │   ├── models/               # SQLAlchemy models
│   │   ├── services/             # Business logic
│   │   └── main_minimal.py       # FastAPI application
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, Footer
│   │   ├── pages/                # Home, Chat, Appointment, Admin
│   │   └── App.tsx
│   ├── tailwind.config.js
│   └── package.json
├── vercel.json                   # Deployment configuration
└── README.md
```

## Deployment

### Vercel Deployment

1. Push to GitHub
2. Import project on [Vercel](https://vercel.com)
3. Add environment variables:
   - `GROQ_API_KEY` - Your Groq API key
   - `REACT_APP_EMAILJS_SERVICE_ID` - EmailJS service ID
   - `REACT_APP_EMAILJS_TEMPLATE_ID` - EmailJS template ID
   - `REACT_APP_EMAILJS_PUBLIC_KEY` - EmailJS public key
4. Deploy!

### GitHub Codespaces

1. Open in Codespaces
2. Run backend: `cd backend && uvicorn app.main_minimal:app --reload --port 8000`
3. Run frontend: `cd frontend && npm start`
4. Access via forwarded ports

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message to AI advisor |
| `POST` | `/api/appointments` | Book an appointment |
| `GET` | `/api/appointments?admin_token=xxx` | List appointments (admin) |
| `GET` | `/api` | Health check |

### Example Request

```bash
curl -X POST https://llm-wealth-advisor.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the best mutual funds for beginners?"}'
```

## Security

- All admin endpoints require authentication
- API keys stored as environment variables
- CORS configured for production domains
- No sensitive data exposed in client code

## About Wallet Wealth LLP

**Wallet Wealth LLP** is a SEBI-registered Investment Advisor (Registration: **INA200015440**) based in Chennai, India.

**Services:**
- Mutual Fund Advisory
- Portfolio Management
- Financial Planning
- Tax Planning
- Retirement Planning
- Insurance Planning

## Contributing

This is a proprietary project for Wallet Wealth LLP.

visit the websit at https://llm-wealth-advisor-51p3f6f3l-msundaras-projects.vercel.app/
