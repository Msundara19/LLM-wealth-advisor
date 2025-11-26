# LLM Wealth Advisor for Wallet Wealth

A sophisticated AI-powered financial advisor chatbot integrated into Wallet Wealth's website, providing personalized investment guidance, portfolio analysis, and financial planning assistance.

## Features

- 🤖 AI-powered financial advisory using OpenAI/Anthropic APIs
- 💼 Portfolio analysis and recommendations
- 📊 Real-time market data integration
- 🔒 Secure authentication and data encryption
- 📱 Responsive web interface
- 🚀 Production-ready deployment setup

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **LangChain** - LLM orchestration and chain management
- **PostgreSQL** - User data and conversation storage
- **Redis** - Caching and session management
- **Celery** - Async task processing

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Socket.io** - Real-time communication

### Infrastructure
- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **GitHub Actions** - CI/CD pipeline
- **AWS/GCP** - Cloud deployment

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-wealth-advisor.git
cd llm-wealth-advisor
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development without Docker

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
llm-wealth-advisor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── .github/
│   └── workflows/
├── docker-compose.yml
└── README.md
```

## Deployment

### GitHub Codespaces
1. Open in Codespaces
2. Run `./scripts/setup-codespace.sh`
3. Access via forwarded ports

### Production Deployment
See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed instructions.

## API Documentation

API documentation is available at `/docs` when running the backend server.

## Security

- All API endpoints require authentication
- Data encryption at rest and in transit
- Regular security audits
- GDPR/financial compliance ready

## Contributing

See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

## License

Proprietary - Wallet Wealth LLP

## Support

For issues or questions, contact: tech@walletwealth.co.in
