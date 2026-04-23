import structlog
from botocore.exceptions import ClientError

from app.config import get_settings
from app.services.s3_service import _get_client

logger = structlog.get_logger(__name__)


def _get_table():
    settings = get_settings()
    dynamodb = _get_client("dynamodb")
    # Use resource API for cleaner item operations
    import boto3
    if settings.aws_profile:
        session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
        resource = session.resource("dynamodb")
    else:
        resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(settings.dynamodb_table)


def save_result(result_id: str, data: dict) -> None:
    """Save analysis result to DynamoDB."""
    table = _get_table()
    # Convert datetime to string if needed
    item = {k: str(v) if hasattr(v, "isoformat") else v for k, v in data.items()}
    item["id"] = result_id
    table.put_item(Item=item)
    logger.info("dynamodb_result_saved", result_id=result_id)


def load_result(result_id: str) -> dict | None:
    """Load a single analysis result from DynamoDB."""
    table = _get_table()
    try:
        response = table.get_item(Key={"id": result_id})
        return response.get("Item")
    except ClientError as e:
        logger.error("dynamodb_load_failed", result_id=result_id, error=str(e))
        return None


def delete_result(result_id: str) -> bool:
    """Delete a single analysis result from DynamoDB."""
    table = _get_table()
    try:
        table.delete_item(Key={"id": result_id})
        logger.info("dynamodb_result_deleted", result_id=result_id)
        return True
    except ClientError as e:
        logger.error("dynamodb_delete_failed", result_id=result_id, error=str(e))
        return False


def list_results(limit: int = 10) -> list[dict]:
    """List most recent analysis results from DynamoDB."""
    table = _get_table()

    response = table.scan(
        ProjectionExpression="id, file_name, overall_score, created_at",
    )

    items = response.get("Items", [])

    # Sort by created_at descending and take limit
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return items[:limit]
