#!/usr/bin/env bash
# ==============================================================================
# DislikeScope-AI — Unified Development Runner for Fedora Linux
# Starts both FastAPI backend and React/Vite frontend with a single command.
# Handles startup order, health verification, and clean shutdown on Ctrl+C.
# ==============================================================================

set -eo pipefail

# ANSI Color codes for clean, readable logs
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

BACKEND_PID=""
FRONTEND_PID=""

# Graceful cleanup on SIGINT (Ctrl+C), SIGTERM, or EXIT
cleanup() {
    trap - SIGINT SIGTERM EXIT
    echo -e "\n${YELLOW}[SHUTDOWN]${NC} Stopping DislikeScope-AI services..."
    
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}[SHUTDOWN]${NC} Terminating frontend server (PID: $FRONTEND_PID)..."
        kill -SIGTERM "$FRONTEND_PID" 2>/dev/null || true
        pkill -P "$FRONTEND_PID" 2>/dev/null || true
    fi

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}[SHUTDOWN]${NC} Terminating backend server (PID: $BACKEND_PID)..."
        kill -SIGTERM "$BACKEND_PID" 2>/dev/null || true
        pkill -P "$BACKEND_PID" 2>/dev/null || true
    fi

    sleep 1
    # Ensure port processes are freed
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 5173/tcp 2>/dev/null || true

    echo -e "${GREEN}[SHUTDOWN]${NC} Both servers stopped cleanly. Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo -e "${CYAN}${BOLD}======================================================${NC}"
echo -e "${CYAN}${BOLD}       DislikeScope-AI — Fedora Single Runner         ${NC}"
echo -e "${CYAN}${BOLD}======================================================${NC}"

# 1. Environment & Path Verification
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[SETUP]${NC} .env not found. Copying default settings from .env.example..."
        cp .env.example .env
    else
        echo -e "${RED}[ERROR]${NC} Neither .env nor .env.example found."
        exit 1
    fi
fi

mkdir -p data logs

# 2. Python Virtual Environment Check
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    echo -e "${YELLOW}[SETUP]${NC} Python virtual environment not found at .venv. Creating..."
    python3 -m venv .venv
    echo -e "${YELLOW}[SETUP]${NC} Installing backend dependencies..."
    "$PROJECT_ROOT/.venv/bin/pip" install --upgrade pip
    "$PROJECT_ROOT/.venv/bin/pip" install -r backend/requirements.txt
fi

# 3. Frontend Node Dependencies Check
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}[SETUP]${NC} Frontend node_modules not found. Installing..."
    (cd frontend && npm install)
fi

# 4. Port Conflict Detection (Prevent Duplicate Servers)
check_port() {
    local port=$1
    local name=$2
    if "$PYTHON_BIN" -c "import socket; s = socket.socket(); res = s.connect_ex(('127.0.0.1', $port)); s.close(); exit(0 if res == 0 else 1)" 2>/dev/null; then
        echo -e "${RED}[ERROR]${NC} Port $port is already in use by another process!"
        echo -e "${YELLOW}[HINT]${NC} Run 'fuser -k $port/tcp' or kill the existing $name process before starting."
        exit 1
    fi
}

check_port 8000 "FastAPI backend"
check_port 5173 "Vite frontend"

# 5. Start Backend Server
echo -e "${CYAN}[BACKEND]${NC} Starting FastAPI backend on http://127.0.0.1:8000..."
"$PYTHON_BIN" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 2>&1 | sed -u 's/^/[BACKEND] /' &
BACKEND_PID=$!

# Wait for backend health endpoint to respond
echo -e "${CYAN}[BACKEND]${NC} Waiting for backend health check..."
BACKEND_READY=false
for i in {1..30}; do
    if curl -s --connect-timeout 1 http://127.0.0.1:8000/api/health | grep -q "healthy"; then
        BACKEND_READY=true
        break
    fi
    sleep 0.5
done

if [ "$BACKEND_READY" = false ]; then
    echo -e "${RED}[ERROR]${NC} Backend failed to respond within 15 seconds. Aborting."
    exit 1
fi
echo -e "${GREEN}[BACKEND]${NC} Backend is online and healthy!"

# 6. Start Frontend Server
echo -e "${CYAN}[FRONTEND]${NC} Starting Vite frontend on http://localhost:5173..."
(cd frontend && npm run dev) 2>&1 | sed -u 's/^/[FRONTEND] /' &
FRONTEND_PID=$!

# Wait for frontend to respond
echo -e "${CYAN}[FRONTEND]${NC} Waiting for frontend dev server..."
FRONTEND_READY=false
for i in {1..30}; do
    if curl -s --connect-timeout 1 http://localhost:5173/ | grep -q "<html"; then
        FRONTEND_READY=true
        break
    fi
    sleep 0.5
done

if [ "$FRONTEND_READY" = false ]; then
    echo -e "${RED}[ERROR]${NC} Frontend failed to respond within 15 seconds. Aborting."
    exit 1
fi

echo -e "\n${GREEN}${BOLD}======================================================${NC}"
echo -e "${GREEN}${BOLD}   ✓ DislikeScope-AI is fully running!               ${NC}"
echo -e "${GREEN}${BOLD}======================================================${NC}"
echo -e "   ${BOLD}Frontend Dashboard:${NC}  ${CYAN}http://localhost:5173${NC}"
echo -e "   ${BOLD}Backend API Docs:${NC}    ${CYAN}http://127.0.0.1:8000/docs${NC}"
echo -e "   ${BOLD}Health Endpoint:${NC}     ${CYAN}http://127.0.0.1:8000/api/health${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "${YELLOW}Press Ctrl+C at any time to stop both servers cleanly.${NC}\n"

# Wait for background processes to keep runner active
wait "$BACKEND_PID" "$FRONTEND_PID"
