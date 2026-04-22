# Job Processor — Full Stack

A three-service job processing system: a FastAPI backend, a Redis-backed worker, and a Node.js frontend. All services run in Docker containers orchestrated with Docker Compose.

---

## Prerequisites

| Tool | Minimum version | Install |
|---|---|---|
| Docker | 24.x | https://docs.docker.com/get-docker/ |
| Docker Compose plugin | 2.x | bundled with Docker Desktop / OrbStack |
| `curl` | any | pre-installed on most systems |
| `jq` | any | `brew install jq` / `apt install jq` |

No other runtimes (Python, Node.js) are needed on the host — everything runs inside containers.

---

## Bring the stack up on a clean machine

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` if you want to change ports or add a Redis password. The defaults work out of the box.

### 3. Start all services

```bash
docker compose up --build -d
```

This builds all three images from source and starts them in dependency order:

```
redis (healthy) → api + worker start → api (healthy) → frontend starts
```

### 4. Verify the stack is healthy

```bash
docker compose ps
```

Expected output — all services should show **healthy**:

```
NAME         IMAGE             STATUS
redis        redis:7-alpine    Up X seconds (healthy)
api          hng-api           Up X seconds (healthy)
worker       hng-worker        Up X seconds (healthy)
frontend     hng-frontend      Up X seconds (healthy)
```

If a service is still `starting`, wait ~30 seconds and run `docker compose ps` again.

### 5. Submit a job and verify end-to-end

```bash
# Submit a job through the frontend
curl -s -X POST http://localhost:3000/submit | jq .
```

Expected:
```json
{ "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" }
```

```bash
# Poll for the result (replace <job_id> with the value above)
curl -s http://localhost:3000/status/<job_id> | jq .
```

Within ~3 seconds the status will change from `queued` to `completed`:
```json
{ "job_id": "...", "status": "completed" }
```

You can also open **http://localhost:3000** in a browser and use the UI.

---

## Stop the stack

```bash
docker compose down
```

To also remove the Redis data volume:

```bash
docker compose down -v
```

---

## Environment variables

All configuration is injected at runtime via environment variables. No secrets are baked into any image.

| Variable | Default | Used by | Description |
|---|---|---|---|
| `REDIS_HOST` | `redis` | api, worker | Redis service hostname |
| `REDIS_PORT` | `6379` | api, worker | Redis port |
| `REDIS_PASSWORD` | *(empty)* | api, worker | Redis auth password |
| `QUEUE_NAME` | `job` | api, worker | Redis list name used as the job queue |
| `FRONTEND_PORT` | `3000` | frontend | Host port the UI is bound to |
| `API_URL` | `http://api:8000` | frontend | Internal URL the frontend uses to reach the API |

See `.env.example` for a ready-to-copy template.

---

## Services

| Service | Port (host) | Description |
|---|---|---|
| `frontend` | 3000 | Express.js UI + proxy |
| `api` | *(internal only)* | FastAPI job submission and status |
| `worker` | *(none)* | Background job processor |
| `redis` | *(internal only)* | Queue and job state store |

Redis is not exposed on the host — it is reachable only by `api` and `worker` over the internal Docker network.

---

## CI/CD Pipeline

The GitHub Actions pipeline runs six stages in strict order on every push:

```
lint → test → build → security scan → integration test → deploy
```

| Stage | What it does |
|---|---|
| **Lint** | flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles) |
| **Test** | pytest unit tests with mocked Redis; coverage report uploaded as artifact |
| **Build** | Builds all three images, tags with git SHA + `latest`, pushes to a local registry service container and to GHCR |
| **Security scan** | Trivy scans all images for CRITICAL CVEs; results uploaded as SARIF to the Security tab |
| **Integration test** | Brings the full stack up inside the runner, submits a job, polls until `completed`, tears down cleanly |
| **Deploy** | Pushes to `main` only — performs a rolling update on the production server; aborts and preserves the old container if the health check does not pass within 60 s |

A failure in any stage prevents all subsequent stages from running.

**Required GitHub secrets for deploy** (Settings → Secrets and variables → Actions):

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | IP or hostname of the production server |
| `DEPLOY_USER` | SSH username |
| `SSH_PRIVATE_KEY` | Private key whose public half is in `~/.ssh/authorized_keys` on the server |
