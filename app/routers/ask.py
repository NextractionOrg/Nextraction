from fastapi import APIRouter, HTTPException
from app.schemas import AskRequest, AskResponse
from app.services.job_manager import job_manager
from app.services.embedder import EmbeddingService
from app.services.generator import GroundedGenerator
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/ask", tags=["ask"])

embedding_service = EmbeddingService()
generator = GroundedGenerator()


@router.post("", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Ask a question against an indexed job"""
    # Check if job exists
    job = job_manager.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if job is done
    if job["state"].value != "done":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not ready. Current state: {job['state'].value}"
        )
    
    # Load vector store
    vector_store = job_manager.get_vector_store(request.job_id)
    if not vector_store:
        raise HTTPException(
            status_code=500,
            detail="Failed to load vector store for this job"
        )
    
    try:
        # Generate query embedding
        query_embedding = await embedding_service.embed_query(request.question)
        
        if len(query_embedding) == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate query embedding"
            )
        
        # Search for relevant chunks
        retrieved_chunks = vector_store.search(query_embedding, top_k=settings.top_k)
        
        # Generate grounded answer
        result = await generator.generate_answer(request.question, retrieved_chunks)
        
        return AskResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")

