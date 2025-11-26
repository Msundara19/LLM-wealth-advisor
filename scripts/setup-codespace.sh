#!/bin/bash

# Setup script for GitHub Codespaces
set -e

echo "🚀 Setting up Wallet Wealth LLM Advisor in Codespaces..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if we're in Codespaces
if [ -z "$CODESPACES" ]; then
    print_error "This script is designed for GitHub Codespaces"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt-get update -qq

# Install PostgreSQL client
print_status "Installing PostgreSQL client..."
sudo apt-get install -y postgresql-client

# Install Redis tools
print_status "Installing Redis tools..."
sudo apt-get install -y redis-tools

# Setup Python environment
print_status "Setting up Python environment..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup Node environment
print_status "Setting up Node environment..."
cd ../frontend
npm install

# Create .env file from example
print_status "Creating environment configuration..."
cd ..
if [ ! -f .env ]; then
    cp .env.example .env
    print_info "Created .env file from template. Please update with your API keys."
fi

# Start services with Docker Compose
print_status "Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
cd backend
source venv/bin/activate
alembic upgrade head

# Create initial data
print_status "Creating initial data..."
python scripts/init_data.py || true

# Start the application
print_status "Starting the application..."
cd ..
docker-compose up -d backend frontend

# Wait for services to start
sleep 5

# Get the Codespaces URL
CODESPACE_NAME="${CODESPACE_NAME:-}"
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}"

if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    BACKEND_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    
    print_status "Setup complete! 🎉"
    echo ""
    echo "Access your application at:"
    echo "  Frontend: $FRONTEND_URL"
    echo "  Backend API: $BACKEND_URL"
    echo "  API Docs: $BACKEND_URL/docs"
else
    print_status "Setup complete! 🎉"
    echo ""
    echo "Access your application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
fi

echo ""
print_info "Remember to update your .env file with API keys!"
print_info "Use 'docker-compose logs -f' to view logs"
print_info "Use 'docker-compose down' to stop all services"
