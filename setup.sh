#!/usr/bin/env bash
# NaviAcess - One-Command Setup Script
# This script sets up both backend and frontend for development

set -e

echo "🧭 NaviAcess Setup Script"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo ""

# Backend Setup
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit backend/.env with your API keys${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
cd ..

echo ""

# Frontend Setup
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

echo "Installing Node dependencies..."
npm install

echo "Creating .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
cd ..

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Run backend: cd backend && source venv/bin/activate && python main.py"
echo "3. Run frontend: cd frontend && npm run dev"
echo "4. Visit http://localhost:5173"
