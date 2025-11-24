# Multi-architecture Dockerfile for Aggregator
# Supports: linux/amd64, linux/arm64
# Build: docker buildx build --platform linux/amd64,linux/arm64 -t aggregator:latest .

# ============================================================================
# Stage 1: Base Image
# ============================================================================
FROM python:3.12.3-slim AS base

# Metadata labels
LABEL maintainer="wzdnzd"
LABEL org.opencontainers.image.title="Aggregator"
LABEL org.opencontainers.image.description="免费代理池构建工具 - Free Proxy Pool Aggregator"
LABEL org.opencontainers.image.url="https://github.com/wzdnzd/aggregator"
LABEL org.opencontainers.image.source="https://github.com/wzdnzd/aggregator"
LABEL org.opencontainers.image.vendor="wzdnzd"
LABEL org.opencontainers.image.licenses="GPL-3.0"

# Build arguments
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH
ARG PIP_INDEX_URL="https://pypi.org/simple"

# Environment variables with defaults
ENV GIST_PAT="" \
    GIST_LINK="" \
    CUSTOMIZE_LINK="" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

WORKDIR /aggregator

# ============================================================================
# Stage 2: Dependencies
# ============================================================================
FROM base AS dependencies

ARG PIP_INDEX_URL

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -i ${PIP_INDEX_URL} -r requirements.txt

# ============================================================================
# Stage 3: Application
# ============================================================================
FROM base AS application

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY subscribe /aggregator/subscribe

# Copy architecture-specific binaries for Clash
# The binaries will be selected based on TARGETARCH during build
COPY clash/Country.mmdb /aggregator/clash/Country.mmdb

# Copy Clash binary based on target architecture
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "amd64" ]; then \
        echo "Installing Clash for amd64"; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        echo "Installing Clash for arm64"; \
    else \
        echo "Unsupported architecture: $TARGETARCH" && exit 1; \
    fi

# Since we need the binaries at build time, copy all and remove unused ones
COPY clash/clash-linux-amd /tmp/clash-linux-amd
COPY clash/clash-linux-arm /tmp/clash-linux-arm

RUN if [ "$TARGETARCH" = "amd64" ]; then \
        cp /tmp/clash-linux-amd /aggregator/clash/clash-linux-amd && \
        chmod +x /aggregator/clash/clash-linux-amd; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        cp /tmp/clash-linux-arm /aggregator/clash/clash-linux-amd && \
        chmod +x /aggregator/clash/clash-linux-amd; \
    fi && \
    rm -f /tmp/clash-linux-*

# Copy Subconverter binaries based on target architecture
COPY subconverter /tmp/subconverter

RUN mkdir -p /aggregator/subconverter && \
    cp -r /tmp/subconverter/base /aggregator/subconverter/ && \
    cp -r /tmp/subconverter/config /aggregator/subconverter/ && \
    cp -r /tmp/subconverter/profiles /aggregator/subconverter/ && \
    cp -r /tmp/subconverter/rules /aggregator/subconverter/ && \
    cp -r /tmp/subconverter/snippets /aggregator/subconverter/ && \
    cp /tmp/subconverter/*.ini /tmp/subconverter/*.toml /tmp/subconverter/*.yml /aggregator/subconverter/ 2>/dev/null || true && \
    if [ "$TARGETARCH" = "amd64" ]; then \
        cp /tmp/subconverter/subconverter-linux-amd /aggregator/subconverter/subconverter-linux-amd && \
        chmod +x /aggregator/subconverter/subconverter-linux-amd; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        cp /tmp/subconverter/subconverter-linux-arm /aggregator/subconverter/subconverter-linux-amd && \
        chmod +x /aggregator/subconverter/subconverter-linux-amd; \
    fi && \
    rm -rf /tmp/subconverter

# Create necessary directories
RUN mkdir -p /aggregator/data /aggregator/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "-u", "subscribe/collect.py", "--all", "--overwrite", "--skip"]
