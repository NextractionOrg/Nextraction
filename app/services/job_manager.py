import uuid
import asyncio
from typing import Dict, Optional
from datetime import datetime
from app.schemas import JobState
from app.utils.logger import logger
from app.services.fetcher import WebFetcher
from app.services.cleaner import ContentCleaner
from app.services.embedder import EmbeddingService
from app.services.vector_store import VectorStore


class JobManager:
    """Manages ingestion jobs and their state"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.embedding_service = EmbeddingService()
    
    def create_job(
        self,
        seed_urls: list,
        domain_allowlist: list,
        max_pages: int,
        max_depth: int,
        user_notes: Optional[str] = None
    ) -> str:
        """Create a new ingestion job"""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "state": JobState.QUEUED,
            "seed_urls": seed_urls,
            "domain_allowlist": domain_allowlist,
            "max_pages": max_pages,
            "max_depth": max_depth,
            "user_notes": user_notes,
            "pages_fetched": 0,
            "pages_indexed": 0,
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created job {job_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        return self.jobs.get(job_id)
    
    def update_job_state(self, job_id: str, state: JobState, **kwargs):
        """Update job state and metadata"""
        if job_id in self.jobs:
            self.jobs[job_id]["state"] = state
            self.jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()
            for key, value in kwargs.items():
                self.jobs[job_id][key] = value
    
    async def process_job(self, job_id: str):
        """Process an ingestion job asynchronously"""
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        try:
            self.update_job_state(job_id, JobState.RUNNING)
            
            # Step 1: Fetch pages
            logger.info(f"Job {job_id}: Starting fetch phase")
            async with WebFetcher() as fetcher:
                pages = await fetcher.crawl(
                    seed_urls=job["seed_urls"],
                    domain_allowlist=job["domain_allowlist"],
                    max_pages=job["max_pages"],
                    max_depth=job["max_depth"]
                )
            
            self.update_job_state(job_id, pages_fetched=len(pages))
            
            if not pages:
                self.update_job_state(job_id, JobState.FAILED, error="No pages fetched")
                return
            
            # Step 2: Clean and chunk
            logger.info(f"Job {job_id}: Starting cleaning phase")
            cleaner = ContentCleaner()
            chunks = cleaner.clean_and_chunk(pages)
            
            if not chunks:
                self.update_job_state(job_id, JobState.FAILED, error="No chunks created")
                return
            
            # Step 3: Generate embeddings
            logger.info(f"Job {job_id}: Starting embedding phase ({len(chunks)} chunks)")
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # Step 4: Index in vector store
            logger.info(f"Job {job_id}: Starting indexing phase")
            vector_store = VectorStore(job_id)
            vector_store.add_chunks(chunks, embeddings)
            vector_store.save()
            
            self.update_job_state(
                job_id,
                JobState.DONE,
                pages_indexed=len(chunks)
            )
            
            logger.info(f"Job {job_id}: Completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job_id}: Failed with error: {error_msg}")
            self.update_job_state(job_id, JobState.FAILED, error=error_msg)
    
    def get_vector_store(self, job_id: str) -> Optional[VectorStore]:
        """Get vector store for a job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        vector_store = VectorStore(job_id)
        if vector_store.load():
            return vector_store
        return None


# Global job manager instance
job_manager = JobManager()

