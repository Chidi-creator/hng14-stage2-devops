# syntax=docker/dockerfile:1

# ── Stage 1: install production dependencies ──────────────────────────────────
FROM node:18-slim AS builder

WORKDIR /build
COPY package*.json ./
# --omit=dev ensures devDependencies never reach the final image
RUN npm ci --omit=dev

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM node:18-slim

WORKDIR /app

# Copy only production node_modules from builder
COPY --from=builder /build/node_modules ./node_modules

# Copy application source — never .env or credentials
COPY app.js .
COPY views/ ./views/

# Non-root user
RUN groupadd --system app && useradd --system --gid app --no-create-home app
USER app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e \
    "require('http').get('http://localhost:3000/', (r) => \
      r.statusCode < 500 ? process.exit(0) : process.exit(1) \
    ).on('error', () => process.exit(1))"

CMD ["node", "app.js"]
