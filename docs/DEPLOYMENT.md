# Deployment Guide for Wallet Wealth LLM Advisor

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [GitHub Codespaces](#github-codespaces)
4. [Production Deployment](#production-deployment)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker & Docker Compose
- Git
- API Keys:
  - OpenAI or Anthropic API key
  - Alpha Vantage API key (for market data)
  - Polygon API key (optional)
- Domain with SSL certificate (for production)

## Local Development

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/llm-wealth-advisor.git
cd llm-wealth-advisor
```

2. **Setup environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (without Docker)

1. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

2. **Frontend setup:**
```bash
cd frontend
npm install
npm start
```

## GitHub Codespaces

### Automatic Setup

1. Open repository in GitHub Codespaces
2. Run the setup script:
```bash
./scripts/setup-codespace.sh
```

3. Access forwarded ports in Codespaces

### Manual Configuration

1. **Install dependencies:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Update with your API keys
```

3. **Start services:**
```bash
docker-compose up -d
```

## Production Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and push images to ECR:**
```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_URI

# Build and tag images
docker build -t llm-advisor-backend ./backend
docker tag llm-advisor-backend:latest $ECR_URI/llm-advisor-backend:latest

docker build -t llm-advisor-frontend ./frontend
docker tag llm-advisor-frontend:latest $ECR_URI/llm-advisor-frontend:latest

# Push images
docker push $ECR_URI/llm-advisor-backend:latest
docker push $ECR_URI/llm-advisor-frontend:latest
```

2. **Deploy with Terraform:**
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

#### Using EC2

1. **Setup EC2 instance:**
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Deploy application:**
```bash
# Clone repository
git clone https://github.com/yourusername/llm-wealth-advisor.git
cd llm-wealth-advisor

# Setup environment
cp .env.example .env
# Configure production settings

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### Google Cloud Platform

1. **Using Cloud Run:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/llm-advisor-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT-ID/llm-advisor-frontend ./frontend

# Deploy to Cloud Run
gcloud run deploy llm-advisor-backend \
  --image gcr.io/PROJECT-ID/llm-advisor-backend \
  --platform managed \
  --region asia-south1

gcloud run deploy llm-advisor-frontend \
  --image gcr.io/PROJECT-ID/llm-advisor-frontend \
  --platform managed \
  --region asia-south1
```

### Kubernetes Deployment

1. **Create namespace:**
```bash
kubectl create namespace wallet-wealth
```

2. **Apply configurations:**
```bash
kubectl apply -f infrastructure/kubernetes/
```

3. **Check deployment:**
```bash
kubectl get pods -n wallet-wealth
kubectl get services -n wallet-wealth
```

### Database Setup

1. **Production database (PostgreSQL):**
```bash
# Run migrations
alembic upgrade head

# Create indexes for performance
psql -U $DB_USER -d $DB_NAME -f infrastructure/sql/indexes.sql
```

2. **Redis configuration:**
```bash
# Set up Redis persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
redis-cli CONFIG SET appendonly yes
```

### SSL/TLS Configuration

1. **Using Let's Encrypt:**
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.walletwealth.co.in -d app.walletwealth.co.in

# Auto-renewal
sudo certbot renew --dry-run
```

2. **Update Nginx configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.walletwealth.co.in;
    
    ssl_certificate /etc/letsencrypt/live/api.walletwealth.co.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.walletwealth.co.in/privkey.pem;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

### Production Configuration

```env
# Set to production
ENVIRONMENT=production
DEBUG=false

# Use strong secrets
JWT_SECRET=<generate-strong-secret>
ENCRYPTION_KEY=<32-byte-key>

# Production database
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname

# Redis cluster
REDIS_URL=redis://elasticache-endpoint:6379

# API Keys (store in AWS Secrets Manager or similar)
OPENAI_API_KEY=<from-secrets-manager>
ANTHROPIC_API_KEY=<from-secrets-manager>

# CORS - Add your domain
CORS_ORIGINS=https://www.walletwealth.co.in,https://app.walletwealth.co.in

# Rate limiting for production
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

## Monitoring

### Health Checks

- Backend health: `https://api.walletwealth.co.in/health`
- Frontend health: `https://app.walletwealth.co.in/health`

### Logging

1. **Application logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

2. **Centralized logging (ELK Stack):**
```yaml
# docker-compose.monitoring.yml
elasticsearch:
  image: elasticsearch:8.11.0
  
logstash:
  image: logstash:8.11.0
  
kibana:
  image: kibana:8.11.0
```

### Metrics

1. **Prometheus metrics:**
- Endpoint: `/metrics`
- Scrape interval: 30s

2. **Grafana dashboards:**
- Import dashboard ID: 12345 (custom LLM metrics)
- Alert rules configured for:
  - High latency (>2s)
  - Error rate (>1%)
  - Memory usage (>80%)

## Security Checklist

- [ ] All secrets in environment variables or secret manager
- [ ] SSL/TLS enabled for all endpoints
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Authentication required for all API endpoints
- [ ] Database connections use SSL
- [ ] Regular security updates applied
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] WAF (Web Application Firewall) enabled

## Backup Strategy

1. **Database backups:**
```bash
# Daily automated backup
pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > backup_$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://wallet-wealth-backups/
```

2. **Redis persistence:**
- AOF (Append Only File) enabled
- RDB snapshots every hour

## Troubleshooting

### Common Issues

1. **Connection refused errors:**
```bash
# Check if services are running
docker-compose ps
# Check logs
docker-compose logs backend
```

2. **Database connection issues:**
```bash
# Test connection
psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "SELECT 1;"
```

3. **API key errors:**
- Verify API keys in `.env`
- Check rate limits on external APIs

4. **Memory issues:**
```bash
# Check container stats
docker stats
# Increase memory limits in docker-compose.yml
```

### Support

- Technical issues: tech@walletwealth.co.in
- Security concerns: security@walletwealth.co.in
- Documentation: https://docs.walletwealth.co.in

## Rollback Procedure

1. **Quick rollback:**
```bash
# Revert to previous version
docker-compose down
git checkout <previous-version>
docker-compose up -d
```

2. **Database rollback:**
```bash
# Restore from backup
gunzip < backup_20240115.sql.gz | psql -U $DB_USER -h $DB_HOST $DB_NAME
```

## Performance Optimization

1. **Enable caching:**
- Redis for session management
- CloudFront/CDN for static assets

2. **Database optimization:**
- Create indexes on frequently queried columns
- Use connection pooling
- Regular VACUUM and ANALYZE

3. **LLM optimization:**
- Use streaming responses
- Implement request batching
- Cache common queries

---

Last updated: January 2024
Version: 1.0.0
