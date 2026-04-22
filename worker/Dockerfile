# syntax=docker/dockerfile:1

# ── Stage 1: install dependencies ────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Pull installed packages from builder
COPY --from=builder /install /usr/local

# Copy only application source — never .env or credentials
COPY worker.py .

# Non-root user
RUN groupadd --system app && useradd --system --gid app --no-create-home app
USER app

# Health check: verify the worker can reach Redis (its sole dependency).
# Uses env vars that are injected at runtime, not baked into the image.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c \
    "import redis, os; \
     r = redis.Redis( \
       host=os.getenv('REDIS_HOST', 'localhost'), \
       port=int(os.getenv('REDIS_PORT', '6379')), \
       password=os.getenv('REDIS_PASSWORD') or None); \
     r.ping()" \
  || exit 1

CMD ["python", "worker.py"]
