from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class IngestRequest(BaseModel):
    seed_urls: List[str] = Field(..., description="List of seed URLs to crawl")
    domain_allowlist: List[str] = Field(..., description="Allowed domains for crawling")
    max_pages: int = Field(20, ge=1, le=1000, description="Maximum number of pages to fetch")
    max_depth: int = Field(2, ge=0, le=10, description="Maximum crawl depth")
    user_notes: Optional[str] = Field(None, description="Optional text tag for this ingestion")


class IngestResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    accepted_pages: int = Field(..., description="Number of pages accepted for processing")


class StatusResponse(BaseModel):
    state: JobState = Field(..., description="Current job state")
    pages_fetched: int = Field(0, description="Number of pages fetched")
    pages_indexed: int = Field(0, description="Number of pages indexed")
    error: Optional[str] = Field(None, description="Error message if failed")


class Citation(BaseModel):
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    chunkid: str = Field(..., description="Unique chunk identifier")
    quote: str = Field(..., max_length=200, description="Short excerpt from the chunk")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AskRequest(BaseModel):
    job_id: str = Field(..., description="Job ID to query against")
    question: str = Field(..., min_length=1, description="Question to answer")


class AskResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(default_factory=list, description="List of citations")
    confidence: Confidence = Field(..., description="Confidence level")
    groundingnotes: str = Field(..., description="Explanation of support level")

