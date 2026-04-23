import uuid
from datetime import datetime, timezone

import structlog

from app.models.responses import AnalysisResult
from app.services import dynamodb_service
from app.services.bedrock_service import analyze_resume
from app.services.textract_service import extract_text

logger = structlog.get_logger(__name__)


async def run_analysis(s3_key: str, job_description: str) -> AnalysisResult:
    """
    Full pipeline:
      1. Textract → extract resume text
      2. Bedrock  → score + suggestions
      3. S3       → save result JSON
    """
    file_name = s3_key.split("/")[-1]
    result_id = str(uuid.uuid4())

    logger.info("analysis_started", s3_key=s3_key, result_id=result_id)

    # Step 1 — Extract text
    resume_text = extract_text(s3_key)

    # Step 2 — Analyze with Bedrock
    analysis = analyze_resume(
        resume_text=resume_text,
        job_description=job_description,
    )

    # Step 3 — Build result
    result = AnalysisResult(
        id=result_id,
        file_name=file_name,
        created_at=datetime.now(timezone.utc),
        job_description=job_description,
        **analysis,
    )

    # Step 4 — Persist to DynamoDB
    dynamodb_service.save_result(result_id, result.model_dump())

    logger.info("analysis_complete", result_id=result_id, score=result.overall_score)
    return result
