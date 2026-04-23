import boto3
import pytest
from moto import mock_aws

from app.services import dynamodb_service


@pytest.fixture(autouse=True)
def mock_dynamodb():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="test-results",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table


class TestSaveResult:
    def test_saves_result(self):
        dynamodb_service.save_result("id-abc", {"overall_score": 70, "file_name": "resume.pdf", "created_at": "2026-01-01"})
        loaded = dynamodb_service.load_result("id-abc")
        assert loaded is not None
        assert loaded["overall_score"] == 70

    def test_saves_result_with_id(self):
        dynamodb_service.save_result("id-xyz", {"overall_score": 50, "file_name": "cv.pdf", "created_at": "2026-01-01"})
        loaded = dynamodb_service.load_result("id-xyz")
        assert loaded["id"] == "id-xyz"


class TestLoadResult:
    def test_returns_none_when_missing(self):
        result = dynamodb_service.load_result("nonexistent-id")
        assert result is None

    def test_loads_saved_result(self):
        dynamodb_service.save_result("id-load", {"overall_score": 88, "file_name": "test.pdf", "created_at": "2026-01-01"})
        result = dynamodb_service.load_result("id-load")
        assert result["overall_score"] == 88


class TestListResults:
    def test_returns_empty_list_when_no_results(self):
        items = dynamodb_service.list_results()
        assert items == []

    def test_returns_saved_results(self):
        dynamodb_service.save_result("id-1", {"overall_score": 60, "file_name": "a.pdf", "created_at": "2026-01-01T00:00:00"})
        dynamodb_service.save_result("id-2", {"overall_score": 80, "file_name": "b.pdf", "created_at": "2026-01-02T00:00:00"})
        items = dynamodb_service.list_results()
        assert len(items) == 2

    def test_respects_limit(self):
        for i in range(5):
            dynamodb_service.save_result(f"id-{i}", {"overall_score": i * 10, "file_name": f"r{i}.pdf", "created_at": f"2026-01-0{i+1}T00:00:00"})
        items = dynamodb_service.list_results(limit=3)
        assert len(items) == 3

    def test_returns_most_recent_first(self):
        dynamodb_service.save_result("old", {"overall_score": 50, "file_name": "old.pdf", "created_at": "2026-01-01T00:00:00"})
        dynamodb_service.save_result("new", {"overall_score": 90, "file_name": "new.pdf", "created_at": "2026-01-10T00:00:00"})
        items = dynamodb_service.list_results()
        assert items[0]["id"] == "new"
