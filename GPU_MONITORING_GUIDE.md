# GPU Monitoring Guide for Mali G610

Complete monitoring reference for ARM Mali G610 GPU and Ollama metrics.

## Understanding Metrics

### GPU Utilization
- **Range:** 0-100%
- **Optimal:** 70-95% during inference
- **Alert:** >90%

### Temperature
- **Idle:** 45-55°C
- **Operating:** 55-75°C
- **Alert:** >80°C
- **Critical:** >95°C

### Memory Usage
- **Light:** 20-40%
- **Moderate:** 40-70%
- **Heavy:** 70-85%
- **Alert:** >85%

## API Endpoints

```bash
# Health check
curl http://localhost:9100/api/health

# Current metrics
curl http://localhost:9100/api/status | jq .

# GPU metrics only
curl http://localhost:9100/api/metrics | jq '.gpu'

# Ollama models
curl http://localhost:9100/api/ollama/models

# Alerts
curl http://localhost:9100/api/alerts

# History (last 60 minutes)
curl "http://localhost:9100/api/history?minutes=60"

# Prometheus metrics
curl http://localhost:9100/metrics
```

## Real-time Monitoring

```bash
# GPU status
watch -n 1 'curl -s http://localhost:9100/api/status | jq .gpu'

# Temperature monitoring
watch -n 2 'curl -s http://localhost:9100/api/metrics | jq .gpu.temperature'

# Full status
./scripts/ollama/status.sh --verbose
```

## Performance Analysis

### GPU-Bound (GPU >90%, CPU <50%)
- GPU is bottleneck
- Optimize model size
- Reduce batch size

### CPU-Bound (CPU >80%, GPU <70%)
- CPU cannot feed GPU
- Consider model conversion

### Memory-Bound (Memory >80%)
- Reduce model size
- Unload unused models

## Alert Configuration

Edit `services/rtpi-gpu-monitor/configs/monitor.yaml`:

```yaml
alerts:
  gpu_utilization_threshold: 90
  temperature_threshold: 80
  memory_threshold: 85
```

## Troubleshooting

```bash
# Service not responding
docker compose restart rtpi-gpu-monitor

# Check logs
docker compose logs rtpi-gpu-monitor

# Restart stack
./scripts/ollama/start.sh --force

# Stop stack
./scripts/ollama/stop.sh

# Verify GPU devices
ls -la /dev/mali0 /dev/dri/*

# Check GPU frequency
cat /sys/class/devfreq/fb000000.gpu/cur_freq
```

## Prometheus Integration

```yaml
scrape_configs:
  - job_name: 'ollama-gpu'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 5s
```

For complete details, see monitoring documentation.
