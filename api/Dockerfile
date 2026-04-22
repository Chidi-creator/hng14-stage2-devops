# syntax=docker/dockerfile:1

# ── Stage 1: install dependencies ────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Pull installed packages from builder; no pip or build tools remain
COPY --from=builder /install /usr/local

# Copy only application source — never .env or credentials
COPY main.py .

# Non-root user
RUN groupadd --system app && useradd --system --gid app --no-create-home app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/openapi.json')" \
  || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
