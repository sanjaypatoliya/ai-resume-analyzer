import json

import boto3
import pytest
from moto import mock_aws

from app.services import s3_service


@pytest.fixture(autouse=True)
def mock_s3():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        yield s3


class TestObjectExists:
    def test_returns_false_when_object_missing(self):
        assert s3_service.object_exists("uploads/missing.pdf") is False

    def test_returns_true_when_object_exists(self, mock_s3):
        mock_s3.put_object(Bucket="test-bucket", Key="uploads/exists.pdf", Body=b"data")
        assert s3_service.object_exists("uploads/exists.pdf") is True


class TestSaveAndLoadResult:
    def test_save_and_load_result(self):
        data = {"overall_score": 75, "file_name": "resume.pdf"}
        s3_service.save_result("test-id-123", data)
        loaded = s3_service.load_result("test-id-123")
        assert loaded["overall_score"] == 75
        assert loaded["file_name"] == "resume.pdf"

    def test_load_result_returns_none_when_missing(self):
        result = s3_service.load_result("nonexistent-id")
        assert result is None


class TestListResults:
    def test_returns_empty_list_when_no_results(self):
        items = s3_service.list_results()
        assert items == []

    def test_returns_results_sorted_by_date(self, mock_s3):
        s3_service.save_result("id-1", {"overall_score": 60, "file_name": "a.pdf", "created_at": "2026-01-01T00:00:00"})
        s3_service.save_result("id-2", {"overall_score": 80, "file_name": "b.pdf", "created_at": "2026-01-02T00:00:00"})
        items = s3_service.list_results(limit=10)
        assert len(items) == 2

    def test_respects_limit(self, mock_s3):
        for i in range(5):
            s3_service.save_result(f"id-{i}", {"overall_score": i * 10, "file_name": f"r{i}.pdf", "created_at": "2026-01-01"})
        items = s3_service.list_results(limit=3)
        assert len(items) == 3
