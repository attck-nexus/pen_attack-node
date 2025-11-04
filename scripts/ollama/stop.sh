#!/bin/bash
# RTPI-PEN: Stop Ollama AI Inference Stack
# Usage: ./scripts/ollama/stop.sh

set -e

# Determine project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }

echo "🛑 RTPI-PEN Ollama Stack Shutdown"
echo ""

log_info "Stopping Ollama stack..."
cd "$PROJECT_ROOT"
docker compose stop rtpi-ollama rtpi-ollama-ui rtpi-gpu-monitor

log_success "Ollama stack stopped"
echo ""
docker ps -a --filter "name=rtpi-ollama" --format "table {{.Names}}\t{{.Status}}"
