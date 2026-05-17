#!/bin/bash
# Post-create script for 47 Doors Boot Camp Codespaces
# This script runs after the container is created

set -e

echo "=========================================="
echo "Setting up 47 Doors Boot Camp Environment"
echo "=========================================="

# Backend setup
echo ""
echo ">>> Installing backend dependencies..."
cd /workspaces/47doors/backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend setup
echo ""
echo ">>> Installing frontend dependencies..."
cd /workspaces/47doors/frontend
npm install

# Install Playwright browsers for E2E testing
echo ""
echo ">>> Installing Playwright browsers..."
npx playwright install --with-deps chromium

# Create .env files from examples if they don't exist
echo ""
echo ">>> Setting up environment files..."
cd /workspaces/47doors/backend
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || echo "USE_MOCK_MODE=true" > .env
    echo "Created backend/.env (mock mode enabled)"
fi

cd /workspaces/47doors/frontend
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || echo "VITE_API_URL=http://localhost:8000" > .env
    echo "Created frontend/.env"
fi

# Verify setup
echo ""
echo ">>> Verifying installation..."
cd /workspaces/47doors

echo "Python version: $(python --version)"
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"

# Run a quick import test
python -c "from backend.app.main import app; print('Backend imports: OK')" || echo "Backend imports: Check requirements"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start Commands:"
echo "  npm run smoke-test     - Run smoke tests to verify setup"
echo "  npm run start:backend  - Start backend API (port 8000)"
echo "  npm run start:frontend - Start frontend dev server (port 5173)"
echo "  npm run start          - Start both services"
echo ""
echo "Lab Navigation:"
echo "  cd labs/00-setup       - Environment setup verification"
echo "  cd labs/01-understanding-agents - Agent concepts"
echo "  cd labs/04-build-rag-pipeline   - RAG implementation"
echo "  cd labs/05-agent-orchestration  - Pipeline wiring"
echo ""
