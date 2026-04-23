import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_aws_services():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        yield


class TestHealthCheck:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestUploadRouter:
    def test_upload_returns_presigned_url(self):
        response = client.post("/api/v1/upload", json={"file_name": "resume.pdf"})
        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data
        assert "s3_key" in data
        assert data["s3_key"].endswith("resume.pdf")

    def test_upload_rejects_non_pdf(self):
        response = client.post("/api/v1/upload", json={
            "file_name": "resume.docx",
            "content_type": "application/docx"
        })
        assert response.status_code == 422

    def test_upload_requires_file_name(self):
        response = client.post("/api/v1/upload", json={})
        assert response.status_code == 422
