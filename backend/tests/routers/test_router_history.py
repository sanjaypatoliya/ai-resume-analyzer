import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.main import app
from app.services import dynamodb_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_aws_services():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="test-results",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield


class TestHistoryRouter:
    def test_returns_empty_list(self):
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_returns_saved_results(self):
        dynamodb_service.save_result("hist-id-1", {
            "overall_score": 70,
            "file_name": "resume.pdf",
            "created_at": "2026-01-01T00:00:00",
        })

        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["overall_score"] == 70

    def test_limit_param(self):
        for i in range(5):
            dynamodb_service.save_result(f"hist-{i}", {
                "overall_score": i * 10,
                "file_name": f"r{i}.pdf",
                "created_at": f"2026-01-0{i+1}T00:00:00",
            })

        response = client.get("/api/v1/history?limit=3")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 3

    def test_get_result_by_id(self):
        dynamodb_service.save_result("detail-id", {
            "id": "detail-id",
            "overall_score": 85,
            "file_name": "resume.pdf",
            "created_at": "2026-01-01T00:00:00",
            "job_description": "Python developer role",
            "categories": [],
            "skills": [],
            "experience": [],
            "education": [],
            "suggestions": [],
        })

        response = client.get("/api/v1/history/detail-id")
        assert response.status_code == 200
        assert response.json()["overall_score"] == 85

    def test_get_result_returns_404_when_missing(self):
        response = client.get("/api/v1/history/nonexistent-id")
        assert response.status_code == 404
