import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestCreateJob:
    def test_returns_200(self):
        with patch("main.r") as mock_r:
            mock_r.lpush.return_value = 1
            mock_r.hset.return_value = True
            resp = client.post("/jobs")
        assert resp.status_code == 200

    def test_response_contains_job_id(self):
        with patch("main.r") as mock_r:
            mock_r.lpush.return_value = 1
            mock_r.hset.return_value = True
            resp = client.post("/jobs")
        assert "job_id" in resp.json()

    def test_job_id_is_valid_uuid(self):
        with patch("main.r") as mock_r:
            mock_r.lpush.return_value = 1
            mock_r.hset.return_value = True
            resp = client.post("/jobs")
        uuid.UUID(resp.json()["job_id"])  # raises ValueError if invalid

    def test_sets_initial_status_to_queued(self):
        with patch("main.r") as mock_r:
            mock_r.lpush.return_value = 1
            mock_r.hset.return_value = True
            resp = client.post("/jobs")
            job_id = resp.json()["job_id"]
            mock_r.hset.assert_called_once_with(
                f"job:{job_id}", "status", "queued"
            )

    def test_pushes_job_id_to_queue(self):
        with patch("main.r") as mock_r:
            mock_r.lpush.return_value = 1
            mock_r.hset.return_value = True
            resp = client.post("/jobs")
            job_id = resp.json()["job_id"]
            args = mock_r.lpush.call_args[0]
            assert job_id in args


class TestGetJob:
    def test_returns_200_when_job_exists(self):
        with patch("main.r") as mock_r:
            mock_r.hget.return_value = b"queued"
            resp = client.get("/jobs/test-id")
        assert resp.status_code == 200

    def test_returns_correct_status(self):
        with patch("main.r") as mock_r:
            mock_r.hget.return_value = b"completed"
            resp = client.get("/jobs/test-id")
        assert resp.json()["status"] == "completed"

    def test_returns_404_when_job_missing(self):
        with patch("main.r") as mock_r:
            mock_r.hget.return_value = None
            resp = client.get("/jobs/nonexistent-id")
        assert resp.status_code == 404

    def test_includes_job_id_in_response(self):
        with patch("main.r") as mock_r:
            mock_r.hget.return_value = b"queued"
            resp = client.get("/jobs/my-job-id")
        assert resp.json()["job_id"] == "my-job-id"
