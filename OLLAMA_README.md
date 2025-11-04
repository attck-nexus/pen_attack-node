# Ollama AI Inference with ARM Mali GPU

Complete guide for Ollama with ARM Mali G610 GPU acceleration on RTPI-PEN.

## Quick Start

```bash
# Start services
./start-ollama.sh

# Pull a model
docker exec rtpi-ollama ollama pull llama2

# Access Web UI
open http://localhost:3000
```

## Access Points

| Service | Local | SSL Gateway |
|---------|-------|-------------|
| Ollama API | http://localhost:11434 | https://demo-ollama.attck-node.net |
| Open WebUI | http://localhost:3000 | https://demo-ai.attck-node.net |
| GPU Monitor | http://localhost:9100 | https://demo-gpu.attck-node.net |

## Model Management

```bash
# Pull models
docker exec rtpi-ollama ollama pull llama2
docker exec rtpi-ollama ollama pull mistral

# List models
docker exec rtpi-ollama ollama list

# Remove model
docker exec rtpi-ollama ollama rm llama2
```

## API Usage

```bash
# Generate completion
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "llama2", "prompt": "Hello!"}'

# List models
curl http://localhost:11434/api/tags
```

## Performance Monitoring

```bash
# Check GPU status
curl http://localhost:9100/api/status | jq .gpu

# Real-time monitoring
watch -n 1 'curl -s http://localhost:9100/api/status | jq .gpu'
```

## Troubleshooting

```bash
# View logs
docker compose logs -f rtpi-ollama

# Restart services
./start-ollama.sh --force

# Check status
./status-ollama.sh --verbose
```

## GPU Optimization

The deployment uses Mali G610 GPU acceleration with:
- Full OpenCL support
- Direct device access (/dev/mali0, /dev/dri/*)
- Performance governor (1 GHz max frequency)
- Resource limits for thermal protection

See GPU_MONITORING_GUIDE.md for details.
