import structlog
from fastapi import APIRouter, HTTPException, Query

from app.models.responses import AnalysisResult, HistoryResponse
from app.services import dynamodb_service

router = APIRouter(prefix="/history", tags=["history"])
logger = structlog.get_logger(__name__)


@router.get("", response_model=HistoryResponse)
async def get_history(limit: int = Query(default=10, ge=1, le=50)) -> HistoryResponse:
    """Return the most recent analysis results stored in DynamoDB."""
    items = dynamodb_service.list_results(limit=limit)
    return HistoryResponse(items=items, total=len(items))  # type: ignore[arg-type]


@router.get("/{result_id}", response_model=AnalysisResult)
async def get_result(result_id: str) -> AnalysisResult:
    """Return full analysis result by ID from DynamoDB."""
    data = dynamodb_service.load_result(result_id)
    if not data:
        raise HTTPException(status_code=404, detail="Result not found")
    return AnalysisResult(**data)  # type: ignore[arg-type]


@router.delete("/{result_id}", status_code=204)
async def delete_result(result_id: str) -> None:
    """Delete an analysis result by ID from DynamoDB."""
    success = dynamodb_service.delete_result(result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found or could not be deleted")
