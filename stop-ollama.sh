#!/bin/bash
# RTPI-PEN: Stop Ollama AI Inference Stack

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }

echo "🛑 RTPI-PEN Ollama Stack Shutdown"
echo ""

log_info "Stopping Ollama stack..."
docker compose stop rtpi-ollama rtpi-ollama-ui rtpi-gpu-monitor

log_success "Ollama stack stopped"
echo ""
docker ps -a --filter "name=rtpi-ollama" --format "table {{.Names}}\t{{.Status}}"
