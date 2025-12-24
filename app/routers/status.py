from fastapi import APIRouter, HTTPException
from app.schemas import StatusResponse
from app.services.job_manager import job_manager

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get the status of an ingestion job"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return StatusResponse(
        state=job["state"],
        pages_fetched=job["pages_fetched"],
        pages_indexed=job["pages_indexed"],
        error=job.get("error")
    )

