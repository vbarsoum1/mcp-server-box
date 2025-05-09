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
# The MCP server talks on stdio; we publish it over HTTP (SSE) on :8000
EXPOSE 8000

# mcp-proxy flags that work today:
#   --host         listen interface   (default 0.0.0.0, but we make it explicit)
#   --port         listen port
#   --stdio        wrap the child process’ stdio
#   --path         optional; lets you change / to /sse, /events, etc.
#   --no-sse       disables streaming and turns the proxy into plain JSON RPC
#
# There are *no* --sse-host / --sse-port flags in current releases.
# Keep --stdio unless you want the proxy to exec a TCP backend instead.

CMD ["mcp-proxy",
     "--host",  "0.0.0.0",
     "--port",  "8000",
     "--stdio",
     # Optional: uncomment the next line if you want to change the path
     # "--path",  "/sse",
     #
     # Optional: uncomment the next line if you prefer non-streaming POST/JSON
     # "--no-sse",
     "--",
     "uv", "run", "src/mcp_server_box.py"]

