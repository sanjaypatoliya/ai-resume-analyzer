import structlog
from fastapi import APIRouter

from app.config import get_settings
from app.models.requests import UploadRequest
from app.models.responses import UploadResponse
from app.services import s3_service

router = APIRouter(prefix="/upload", tags=["upload"])
logger = structlog.get_logger(__name__)


@router.post("", response_model=UploadResponse)
async def get_presigned_upload_url(body: UploadRequest) -> UploadResponse:
    """
    Returns a presigned S3 POST URL.
    The browser uploads the PDF directly to S3 — file bytes never pass through this API.
    """
    result = s3_service.generate_presigned_upload_url(body.file_name)

    logger.info("upload_url_issued", s3_key=result["s3_key"])

    return UploadResponse(
        upload_url=result["upload_url"],
        upload_fields=result["upload_fields"],
        s3_key=result["s3_key"],
        expires_in=get_settings().s3_presigned_url_expiry,
    )
