FROM ollama/ollama:latest

# Install system dependencies for Mali GPU support
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Set up Mali GPU environment
ENV LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libmali-x11:/usr/lib/aarch64-linux-gnu:${LD_LIBRARY_PATH}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Expose Ollama API port
EXPOSE 11434

# Use default Ollama entrypoint
CMD ["/bin/ollama", "serve"]
