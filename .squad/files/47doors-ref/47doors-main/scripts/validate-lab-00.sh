#!/bin/bash
# Lab 00 Quick Validation Script
# Usage: bash scripts/validate-lab-00.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    47 Doors - Lab 00 Environment Validation Script        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS="${GREEN}✅ PASS${NC}"
FAIL="${RED}❌ FAIL${NC}"
WARN="${YELLOW}⚠️  WARN${NC}"

# Track overall status
OVERALL_STATUS=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Python Version Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "   Found: Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    echo -e "   Status: $PASS (Required: Python 3.11+)"
else
    echo -e "   Status: $FAIL (Required: Python 3.11+, Found: $PYTHON_VERSION)"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Node.js Version Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

echo "   Found: Node.js $NODE_VERSION"

if [ "$NODE_MAJOR" -ge 18 ]; then
    echo -e "   Status: $PASS (Required: Node.js 18+)"
else
    echo -e "   Status: $FAIL (Required: Node.js 18+, Found: $NODE_VERSION)"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. GitHub Codespaces Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -z "$CODESPACE_NAME" ]; then
    echo -e "   Status: $WARN (Not running in Codespaces)"
    echo "   Note: This is OK for local development"
else
    echo "   Codespace Name: $CODESPACE_NAME"
    echo "   Frontend URL: https://$CODESPACE_NAME-5173.app.github.dev"
    echo "   Backend URL:  https://$CODESPACE_NAME-8000.app.github.dev"
    echo -e "   Status: $PASS"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Backend Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "backend/.venv" ]; then
    echo "   Location: backend/.venv"
    echo -e "   Status: $PASS"

    # Check if activated
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "   Active: Yes"
    else
        echo "   Active: No (activate with: source backend/.venv/bin/activate)"
    fi
else
    echo -e "   Status: $FAIL (Virtual environment not found)"
    echo "   Fix: cd backend && python -m venv .venv"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Backend Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
    FASTAPI_VERSION=$(pip show fastapi 2>/dev/null | grep Version | awk '{print $2}')

    if [ -n "$FASTAPI_VERSION" ]; then
        echo "   FastAPI: $FASTAPI_VERSION"
        echo -e "   Status: $PASS"
    else
        echo -e "   Status: $FAIL (FastAPI not installed)"
        echo "   Fix: cd backend && pip install -r requirements.txt"
        OVERALL_STATUS=1
    fi
else
    echo -e "   Status: $FAIL (Cannot check - venv missing)"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Frontend Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "frontend/node_modules" ]; then
    echo "   Location: frontend/node_modules"

    if [ -f "frontend/node_modules/react/package.json" ]; then
        REACT_VERSION=$(cat frontend/node_modules/react/package.json | grep '"version"' | head -1 | awk -F'"' '{print $4}')
        echo "   React: $REACT_VERSION"
    fi

    echo -e "   Status: $PASS"
else
    echo -e "   Status: $FAIL (node_modules not found)"
    echo "   Fix: cd frontend && npm install"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. CORS Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "backend/.env" ]; then
    echo "   File: backend/.env exists"

    if grep -q "CORS_ORIGINS" backend/.env; then
        CORS_LINE=$(grep "CORS_ORIGINS" backend/.env)
        echo "   CORS_ORIGINS: Found"

        if [ -n "$CODESPACE_NAME" ]; then
            if echo "$CORS_LINE" | grep -q "$CODESPACE_NAME"; then
                echo "   Codespaces URL: Configured correctly"
                echo -e "   Status: $PASS"
            else
                echo -e "   Status: $WARN (Codespace URL not in CORS_ORIGINS)"
                echo "   Expected: https://$CODESPACE_NAME-5173.app.github.dev"
                echo "   Fix: Update CORS_ORIGINS in backend/.env"
            fi
        else
            echo -e "   Status: $PASS (Local development)"
        fi
    else
        echo -e "   Status: $FAIL (CORS_ORIGINS not found)"
        echo "   Fix: Add CORS_ORIGINS to backend/.env"
        OVERALL_STATUS=1
    fi
else
    echo -e "   Status: $FAIL (backend/.env not found)"
    echo "   Fix: cp backend/.env.example backend/.env"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Mock Mode Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "backend/.env" ]; then
    if grep -q "MOCK_MODE" backend/.env; then
        MOCK_MODE=$(grep "MOCK_MODE" backend/.env | cut -d= -f2)
        echo "   MOCK_MODE: $MOCK_MODE"

        if [ "$MOCK_MODE" = "true" ]; then
            echo -e "   Status: $PASS (Mock mode enabled - no Azure credentials needed)"
        else
            echo -e "   Status: $WARN (Mock mode disabled - Azure credentials required)"
        fi
    else
        echo -e "   Status: $WARN (MOCK_MODE not found, assuming false)"
    fi
else
    echo -e "   Status: $FAIL (backend/.env not found)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. Lab 00 Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "labs/00-setup/README.md" ]; then
    README_SIZE=$(wc -c < "labs/00-setup/README.md")
    echo "   File: labs/00-setup/README.md"
    echo "   Size: $README_SIZE bytes"

    if [ $README_SIZE -gt 500 ]; then
        echo -e "   Status: $PASS (Comprehensive documentation)"
    else
        echo -e "   Status: $WARN (Documentation seems short)"
    fi
else
    echo -e "   Status: $FAIL (README.md not found)"
    OVERALL_STATUS=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. Port Availability (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v lsof >/dev/null 2>&1; then
    PORT_8000=$(lsof -ti:8000 || echo "")
    PORT_5173=$(lsof -ti:5173 || echo "")

    if [ -n "$PORT_8000" ]; then
        echo "   Port 8000: In use (backend running)"
    else
        echo "   Port 8000: Available"
    fi

    if [ -n "$PORT_5173" ]; then
        echo "   Port 5173: In use (frontend running)"
    else
        echo "   Port 5173: Available"
    fi

    echo -e "   Status: $PASS (Ports checked)"
else
    echo "   lsof not available - skipping port check"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  VALIDATION SUMMARY                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your environment is ready for Lab 00!"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "  2. Start frontend: cd frontend && npm run dev"
    echo "  3. Access frontend at: https://$CODESPACE_NAME-5173.app.github.dev"
    echo ""
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Please review the output above and fix the issues before proceeding."
    echo ""
    exit 1
fi

exit 0
