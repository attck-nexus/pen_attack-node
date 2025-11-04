FROM ghcr.io/open-webui/open-webui:main

# Environment variables for Ollama connection
ENV OLLAMA_API_BASE_URL=http://rtpi-ollama:11434
ENV OLLAMA_BASE_URL=http://rtpi-ollama:11434
ENV WEBUI_SECRET_KEY=rtpi-pen-secret-key-2025

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Expose web UI port (8080 is standard for Open WebUI)
EXPOSE 8080

# Use default entrypoint from base image
