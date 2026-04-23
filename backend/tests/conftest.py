import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    """Clear real AWS profile and inject fake credentials for moto."""
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("DYNAMODB_TABLE", "test-results")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL_ID", "claude-sonnet-4-6")

    from app.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="function")
def test_client():
    """FastAPI test client."""
    from app.main import app
    return TestClient(app)
