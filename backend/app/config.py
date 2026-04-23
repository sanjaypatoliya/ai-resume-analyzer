from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"

    # AWS — use profile-based auth (recommended) or explicit keys
    aws_region: str = "us-east-1"
    aws_profile: str | None = None          # e.g. "resume-parser"
    aws_access_key_id: str | None = None    # optional — use profile instead
    aws_secret_access_key: str | None = None
    aws_endpoint_url: str | None = None     # LocalStack only

    # S3
    s3_bucket: str = "resume-parser-dev"
    s3_presigned_url_expiry: int = 300

    # Bedrock
    bedrock_model_id: str = "anthropic.claude-sonnet-4-6"
    bedrock_region: str = "us-east-1"

    # DynamoDB
    dynamodb_table: str = "resume-analyzer-results"

    # Anthropic API (fallback when Bedrock not available)
    anthropic_api_key: str = ""
    anthropic_model_id: str = "claude-sonnet-4-6"

    # Hugging Face
    hf_api_token: str = ""
    hf_model_id: str = "Qwen/Qwen2.5-7B-Instruct"

    @property
    def is_local(self) -> bool:
        return self.aws_endpoint_url is not None


@lru_cache
def get_settings() -> Settings:
    return Settings()
