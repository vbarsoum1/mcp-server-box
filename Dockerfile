# ─────────────────────────────────────────────────────────────
# Dockerfile – MCP Server for Box on Coolify
# ─────────────────────────────────────────────────────────────

############## 1️⃣  Base image ##################################################
FROM python:3.13-slim

############## 2️⃣  OS packages #################################################
# ‘uv’ sometimes needs headers; cryptography needs build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

############## 3️⃣  Python tooling #############################################
#  - uv: fast installer / virtual-env replacement
#  - mcp-proxy: converts stdio MCP server → SSE endpoint
RUN pip install --no-cache-dir \
      uv==0.7.* \
      mcp-proxy==0.3.*

############## 4️⃣  Project files & dependencies ###############################
WORKDIR /app

# -- Copy only dependency manifests first so Docker layer caching works  --
COPY pyproject.toml uv.lock* /app/

# -- Install deps exactly as locked, fall back to resolving from project ------
# Use 'uv sync' without explicit lockfile argument; it finds uv.lock in CWD
RUN if [ -f uv.lock ]; then \
        uv sync; \
    else \
        uv pip install .; \
    fi

# -- Now copy the rest of the source code -------------------------------------
COPY . /app

############## 5️⃣  Runtime config #############################################
# The MCP server itself speaks stdio; we expose it via SSE on :8000
EXPOSE 8000

# Corrected CMD arguments for mcp-proxy:
#   --sse-host 0.0.0.0 to listen on all interfaces
#   --sse-port (was --port)
#   --stdio flag removed (unrecognized by this mcp-proxy version)
CMD ["mcp-proxy", "--sse-host", "0.0.0.0", "--sse-port", "8000", "--", "uv", "run", "src/mcp_server_box.py"]

