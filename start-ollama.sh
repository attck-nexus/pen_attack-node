#!/bin/bash
# RTPI-PEN: Start Ollama AI Inference Stack
# Usage: ./start-ollama.sh [--force]

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

FORCE=false
[[ "$1" == "--force" ]] && FORCE=true

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

echo "🚀 RTPI-PEN Ollama Stack Startup"
echo "=================================="
echo ""

# Check if already running
if [ "$FORCE" != "true" ]; then
    if docker ps --filter "name=rtpi-ollama" --filter "status=running" | grep -q rtpi-ollama; then
        log_success "Ollama stack is already running!"
        docker ps --filter "name=rtpi-ollama" --format "table {{.Names}}\t{{.Status}}"
        exit 0
    fi
fi

# Check port 11434
if ! sudo lsof -ti:11434 > /dev/null 2>&1; then
    log_success "Port 11434 is available"
else
    log_warn "Port 11434 is in use"
    conflicting=$(docker ps -q --filter "publish=11434")
    if [ -n "$conflicting" ]; then
        log_info "Stopping conflicting container..."
        docker stop $conflicting
        sleep 2
    fi
fi

log_info "Starting Ollama stack..."
sudo docker compose up -d rtpi-ollama rtpi-ollama-ui rtpi-gpu-monitor

sleep 5
log_info "Waiting for services..."

for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \
       curl -s http://localhost:3000/ > /dev/null 2>&1 && \
       curl -s http://localhost:9100/api/health > /dev/null 2>&1; then
        log_success "All services ready!"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "=================================="
log_success "Ollama Stack Started"
echo "=================================="
echo ""
echo "  🤖 Ollama API:  http://localhost:11434"
echo "  🎨 Web UI:      http://localhost:3000"
echo "  📊 Monitor:     http://localhost:9100"
echo ""
