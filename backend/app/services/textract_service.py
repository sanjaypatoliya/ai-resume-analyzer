import io
import time

import structlog

from app.config import get_settings
from app.services.s3_service import _get_client

logger = structlog.get_logger(__name__)

MAX_POLL_ATTEMPTS = 60
POLL_INTERVAL_SECONDS = 2


def extract_text(s3_key: str) -> str:
    """
    Extract plain text from a PDF stored in S3.

    Primary: AWS Textract async (StartDocumentTextDetection).
    Fallback: pypdf local extraction if Textract times out.
    """
    try:
        return _extract_via_textract(s3_key)
    except RuntimeError as e:
        if "timed out" in str(e):
            logger.warning("textract_timeout_fallback", s3_key=s3_key)
            return _extract_via_pypdf(s3_key)
        raise


def _extract_via_textract(s3_key: str) -> str:
    """Async Textract extraction — supports all PDF types and multi-page."""
    settings = get_settings()
    textract = _get_client("textract")

    logger.info("textract_start", s3_key=s3_key)

    try:
        response = textract.start_document_text_detection(
            DocumentLocation={
                "S3Object": {
                    "Bucket": settings.s3_bucket,
                    "Name": s3_key,
                }
            }
        )
    except Exception as e:
        logger.error("textract_start_failed", s3_key=s3_key, error=str(e))
        raise RuntimeError(f"Text extraction failed: {e}") from e

    job_id = response["JobId"]
    logger.info("textract_job_started", job_id=job_id)

    for attempt in range(MAX_POLL_ATTEMPTS):
        result = textract.get_document_text_detection(JobId=job_id)
        status = result["JobStatus"]

        if status == "SUCCEEDED":
            break
        elif status == "FAILED":
            raise RuntimeError("Textract job failed")

        logger.info("textract_polling", attempt=attempt + 1, status=status)
        time.sleep(POLL_INTERVAL_SECONDS)
    else:
        raise RuntimeError("Textract job timed out")

    # Collect all pages
    all_blocks = list(result.get("Blocks", []))
    next_token = result.get("NextToken")
    while next_token:
        page_result = textract.get_document_text_detection(JobId=job_id, NextToken=next_token)
        all_blocks.extend(page_result.get("Blocks", []))
        next_token = page_result.get("NextToken")

    lines = [block["Text"] for block in all_blocks if block["BlockType"] == "LINE"]
    extracted = "\n".join(lines)
    logger.info("textract_complete", job_id=job_id, line_count=len(lines))

    if not extracted.strip():
        raise RuntimeError("No text could be extracted from the document")

    return extracted


def _extract_via_pypdf(s3_key: str) -> str:
    """Local PDF extraction via pypdf — used as fallback when Textract times out."""
    from pypdf import PdfReader

    settings = get_settings()
    s3 = _get_client("s3")

    logger.info("pypdf_fallback_start", s3_key=s3_key)

    try:
        response = s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
        pdf_bytes = response["Body"].read()
    except Exception as e:
        raise RuntimeError(f"Failed to download PDF from S3: {e}") from e

    reader = PdfReader(io.BytesIO(pdf_bytes))
    lines = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines.append(text)

    extracted = "\n".join(lines)
    logger.info("pypdf_fallback_complete", pages=len(reader.pages), chars=len(extracted))

    if not extracted.strip():
        raise RuntimeError("No text could be extracted from the document")

    return extracted
