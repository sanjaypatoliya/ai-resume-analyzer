import structlog
from fastapi import APIRouter, HTTPException

from app.models.requests import AnalyzeRequest
from app.models.responses import AnalysisResult
from app.services import s3_service
from app.services.analysis_service import run_analysis

router = APIRouter(prefix="/analyze", tags=["analyze"])
logger = structlog.get_logger(__name__)


@router.post("", response_model=AnalysisResult)
async def analyze_resume(body: AnalyzeRequest) -> AnalysisResult:
    """
    Orchestrates the full analysis pipeline:
    1. Verify PDF exists in S3
    2. Extract text via Textract
    3. Analyze with Bedrock (Claude)
    4. Save result to S3
    5. Return structured result
    """
    if not s3_service.object_exists(body.s3_key):
        raise HTTPException(status_code=404, detail="Resume not found in storage. Please re-upload.")

    try:
        result = await run_analysis(
            s3_key=body.s3_key,
            job_description=body.job_description,
        )
    except RuntimeError as e:
        logger.error("analysis_failed", s3_key=body.s3_key, error=str(e))
        raise HTTPException(status_code=422, detail=str(e))

    return result
