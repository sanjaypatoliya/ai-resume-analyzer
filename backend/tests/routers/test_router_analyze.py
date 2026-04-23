from unittest.mock import patch

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.main import app

client = TestClient(app)

MOCK_ANALYSIS_RESULT = {
    "overall_score": 75,
    "categories": [
        {"name": "Skills Match", "score": 80, "rationale": "Good"},
        {"name": "Experience Level", "score": 70, "rationale": "OK"},
        {"name": "Education", "score": 90, "rationale": "Great"},
        {"name": "Keywords", "score": 65, "rationale": "Fair"},
        {"name": "ATS Formatting", "score": 75, "rationale": "Clean"},
    ],
    "skills": ["Python", "FastAPI"],
    "experience": [{"title": "Dev", "company": "Acme", "duration": "2021-2024"}],
    "education": [{"degree": "BS CS", "institution": "Uni", "year": "2020"}],
    "suggestions": ["Add more keywords"],
}


@pytest.fixture(autouse=True)
def mock_aws_services():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="test-results",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield


class TestAnalyzeRouter:
    def test_returns_404_when_file_missing(self):
        response = client.post("/api/v1/analyze", json={
            "s3_key": "uploads/nonexistent/resume.pdf",
            "job_description": "We need a Python developer with FastAPI experience"
        })
        assert response.status_code == 404

    def test_returns_422_when_job_description_empty(self):
        response = client.post("/api/v1/analyze", json={
            "s3_key": "uploads/uuid/resume.pdf",
            "job_description": ""
        })
        assert response.status_code == 422

    def test_full_pipeline_returns_result(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket="test-bucket", Key="uploads/uuid/resume.pdf", Body=b"fake pdf")

        with patch("app.services.analysis_service.extract_text", return_value="Resume text content"), \
             patch("app.services.analysis_service.analyze_resume", return_value=MOCK_ANALYSIS_RESULT):
            response = client.post("/api/v1/analyze", json={
                "s3_key": "uploads/uuid/resume.pdf",
                "job_description": "We need a Python developer with FastAPI experience"
            })

        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] == 75
        assert "id" in data
        assert data["file_name"] == "resume.pdf"

    def test_result_is_saved_to_dynamodb(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket="test-bucket", Key="uploads/uuid/resume.pdf", Body=b"fake pdf")

        with patch("app.services.analysis_service.extract_text", return_value="Resume text content"), \
             patch("app.services.analysis_service.analyze_resume", return_value=MOCK_ANALYSIS_RESULT):
            response = client.post("/api/v1/analyze", json={
                "s3_key": "uploads/uuid/resume.pdf",
                "job_description": "We need a Python developer"
            })

        result_id = response.json()["id"]
        history = client.get("/api/v1/history")
        ids = [item["id"] for item in history.json()["items"]]
        assert result_id in ids
