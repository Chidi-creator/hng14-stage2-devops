# Fix Log

1. File: `api/main.py:1`
Problem: API returned a JSON error payload for missing jobs without an HTTP error status, which incorrectly produced HTTP 200 for not-found resources.
Change: Imported `HTTPException` and changed the missing-job branch to `raise HTTPException(status_code=404, detail="Job not found")`.

2. File: `api/main.py:11-16`
Problem: Redis connection was hardcoded to `localhost:6379`. This works locally but breaks in containers where Redis is reached via service DNS (for example `redis`) and may require auth.
Change: Added env-driven Redis configuration (`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`) and used it when creating the Redis client.

3. File: `api/main.py:14` and `api/main.py:21`
Problem: Queue name was hardcoded to `job`, preventing consistent runtime configuration across environments.
Change: Added `QUEUE_NAME` from environment (default `job`) and used it for enqueue operations.

4. File: `api/main.py:5-7` and `api/requirements.txt:4`
Problem: Environment values in `api/.env` were not loaded by the API process, so local/dev configuration in that file was ignored.
Change: Added `python-dotenv` dependency, imported `load_dotenv`, and called `load_dotenv()` during startup.

5. File: `worker/worker.py:5-10`
Problem: Worker Redis connection was hardcoded to `localhost:6379` with no password support, which fails in containerized multi-service networks and secured Redis setups.
Change: Switched to env-driven Redis config (`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`) for the worker Redis client.

6. File: `worker/worker.py:8` and `worker/worker.py:19`
Problem: Worker consumed from hardcoded queue `job`, which can drift from API queue configuration across deployments.
Change: Added env-driven `QUEUE_NAME` and used it in `brpop`.

7. File: `worker/worker.py:4`
Problem: Unused `signal` import increased noise and suggests non-existent signal handling.
Change: Removed unused import.

8. File: `frontend/app.js:6`
Problem: Frontend server used hardcoded API URL `http://localhost:8000`. Inside a container this points to itself, not the API service.
Change: Made API target configurable via `process.env.API_URL` with local fallback to `http://localhost:8000`.
