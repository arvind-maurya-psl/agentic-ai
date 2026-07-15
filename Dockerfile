# Multi-stage Dockerfile for Agentic AI Application
# Optimized for production deployment

# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 agentic && \
    mkdir -p /app /var/log/app && \
    chown -R agentic:agentic /app /var/log/app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/agentic/.local

# Update PATH
ENV PATH=/home/agentic/.local/bin:$PATH

# Copy application code
COPY --chown=agentic:agentic src/ ./src/
COPY --chown=agentic:agentic infrastructure/ ./infrastructure/
COPY --chown=agentic:agentic requirements.txt .

# Switch to non-root user
USER agentic

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from agentic_ai.config import get_config; get_config()" || exit 1

# Expose port (if needed for API)
EXPOSE 8000

# Default command
CMD ["python", "-m", "agentic_ai.app"]
