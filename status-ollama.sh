#!/bin/bash
# RTPI-PEN: Ollama Stack Status

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

VERBOSE=false
[[ "$1" == "--verbose" || "$1" == "-v" ]] && VERBOSE=true

echo "📊 RTPI-PEN Ollama Stack Status"
echo "================================"
echo ""

# Container status
docker ps -a --filter "name=rtpi-ollama" --filter "name=rtpi-gpu-monitor" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔗 Access Points:"
echo "  🤖 Ollama API:  http://localhost:11434"
echo "  🎨 Web UI:      http://localhost:3000"
echo "  📊 Monitor:     http://localhost:9100"
echo ""

if [ "$VERBOSE" = "true" ]; then
    echo "📋 Detailed Status:"
    echo "---"
    curl -s http://localhost:9100/api/status 2>/dev/null | jq '.' || log_error "Monitor API not responding"
fi

echo "================================"
