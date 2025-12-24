from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas import IngestRequest, IngestResponse
from app.services.job_manager import job_manager
from app.utils.logger import logger

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse, status_code=202)
async def ingest(
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """Start an ingestion job"""
    try:
        job_id = job_manager.create_job(
            seed_urls=request.seed_urls,
            domain_allowlist=request.domain_allowlist,
            max_pages=request.max_pages,
            max_depth=request.max_depth,
            user_notes=request.user_notes
        )
        
        # Start background processing
        background_tasks.add_task(job_manager.process_job, job_id)
        
        # Count accepted pages (will be updated as job progresses)
        accepted_pages = len(request.seed_urls)
        
        logger.info(f"Started ingestion job {job_id} with {accepted_pages} seed URLs")
        
        return IngestResponse(
            job_id=job_id,
            accepted_pages=accepted_pages
        )
        
    except Exception as e:
        logger.error(f"Error creating ingestion job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

