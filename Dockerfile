# ─────────────────────────────────────────────────────────────
# Dockerfile for box-community/mcp-server-box on Coolify
# ─────────────────────────────────────────────────────────────
# 1. Base image ─ Python 3.13 slim
FROM python:3.13-slim

# 2. Install system helpers that uv or cryptography may need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

# 3. Install uv + mcp-proxy
#    (uv is published on PyPI, so a single pip line is enough)
RUN pip install --no-cache-dir \
      uv==0.7.* \
      mcp-proxy==0.3.*

# 4. Create work dir and copy project
WORKDIR /app
COPY . /app

# 5. Lock + install deps the way the README expects
# NEW – prefer the lock file, fall back to “install this project”
RUN if [ -f uv.lock ]; then \
        uv pip install -r uv.lock; \
    else \
        uv pip install .; \
    fi


# 6. Expose the HTTP / SSE port we will proxy to
EXPOSE 8000

# 7. Start the stdio MCP server and immediately
#    proxy it to an SSE endpoint on :8000
CMD ["mcp-proxy", "--port", "8000", "--stdio", "--", "uv", "run", "src/mcp_server_box.py"]
