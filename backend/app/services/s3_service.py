import json
import uuid
from datetime import datetime, timezone

import boto3
import structlog
from botocore.exceptions import ClientError

from app.config import get_settings

logger = structlog.get_logger(__name__)


def _get_client(service: str):  # type: ignore[no-untyped-def]
    settings = get_settings()

    # Use named profile if set, otherwise fall back to explicit keys or env defaults
    if settings.aws_profile:
        session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
        kwargs = {"endpoint_url": settings.aws_endpoint_url} if settings.aws_endpoint_url else {}
        return session.client(service, **kwargs)

    kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client(service, **kwargs)


def generate_presigned_upload_url(file_name: str) -> dict[str, str]:
    """Generate a presigned POST URL for direct browser-to-S3 upload."""
    settings = get_settings()
    s3 = _get_client("s3")

    key = f"uploads/{uuid.uuid4()}/{file_name}"

    presigned = s3.generate_presigned_post(
        Bucket=settings.s3_bucket,
        Key=key,
        Fields={"Content-Type": "application/pdf"},
        Conditions=[
            {"Content-Type": "application/pdf"},
            ["content-length-range", 1, 10 * 1024 * 1024],  # max 10MB
        ],
        ExpiresIn=settings.s3_presigned_url_expiry,
    )

    logger.info("presigned_url_generated", key=key)
    return {
        "upload_url": presigned["url"],
        "upload_fields": presigned["fields"],
        "s3_key": key,
    }


def object_exists(key: str) -> bool:
    """Check whether an object exists in S3."""
    settings = get_settings()
    s3 = _get_client("s3")
    try:
        s3.head_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except ClientError:
        return False


def save_result(result_id: str, data: dict) -> None:  # type: ignore[type-arg]
    """Persist analysis result JSON to S3."""
    settings = get_settings()
    s3 = _get_client("s3")
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=f"results/{result_id}.json",
        Body=json.dumps(data, default=str),
        ContentType="application/json",
    )
    logger.info("result_saved", result_id=result_id)


def load_result(result_id: str) -> dict | None:  # type: ignore[type-arg]
    """Load analysis result JSON from S3."""
    settings = get_settings()
    s3 = _get_client("s3")
    try:
        response = s3.get_object(
            Bucket=settings.s3_bucket,
            Key=f"results/{result_id}.json",
        )
        return json.loads(response["Body"].read())
    except ClientError:
        return None


def list_results(limit: int = 10) -> list[dict]:  # type: ignore[type-arg]
    """List recent analysis results from S3."""
    settings = get_settings()
    s3 = _get_client("s3")

    response = s3.list_objects_v2(
        Bucket=settings.s3_bucket,
        Prefix="results/",
        MaxKeys=limit,
    )

    items = []
    for obj in sorted(
        response.get("Contents", []),
        key=lambda x: x["LastModified"],
        reverse=True,
    )[:limit]:
        result_id = obj["Key"].replace("results/", "").replace(".json", "")
        data = load_result(result_id)
        if data:
            items.append({
                "id": result_id,
                "file_name": data.get("file_name", "unknown"),
                "overall_score": data.get("overall_score", 0),
                "created_at": data.get("created_at", datetime.now(timezone.utc).isoformat()),
            })

    return items
