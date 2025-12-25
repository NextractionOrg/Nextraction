# Design Document: NexTraction Web RAG Pipeline

## Overview

This document describes the design decisions, architecture, and trade-offs for the NexTraction Web RAG pipeline.

## Architecture

### High-Level Flow

```
User Request → API Endpoint → Background Job → Fetch → Clean → Embed → Index → Query → Generate → Response
```

### Components

1. **Web Fetcher**: Crawls web pages with domain restrictions and depth limits
2. **Content Cleaner**: Converts HTML to clean text and chunks it
3. **Embedding Service**: Generates vector embeddings for chunks
4. **Vector Store**: FAISS-based index for semantic search
5. **Grounded Generator**: LLM-powered answer generation with citations
6. **Job Manager**: Orchestrates the ingestion pipeline

## Design Decisions

### 1. Vector Store: FAISS vs. pgvector

**Choice**: FAISS (in-memory with disk persistence)

**Rationale**:
- **Simplicity**: No database setup required
- **Performance**: Fast similarity search for moderate datasets
- **Portability**: Easy to serialize and move between environments
- **Trade-off**: Not suitable for very large datasets or multi-tenant scenarios

**Alternative Considered**: pgvector
- Better for production at scale
- Supports concurrent access
- More complex setup

### 2. Embedding Provider: OpenAI vs. Local

**Choice**: Configurable (OpenAI default, local fallback)

**Rationale**:
- **OpenAI**: High quality, consistent embeddings, requires API key
- **Local (sentence-transformers)**: No API costs, works offline, slightly lower quality
- **Flexibility**: Users can choose based on requirements

### 3. Chunking Strategy

**Choice**: Fixed-size chunks with overlap, sentence-boundary aware

**Rationale**:
- **Fixed-size**: Predictable embedding costs and retrieval behavior
- **Overlap**: Prevents information loss at chunk boundaries
- **Sentence-aware**: Better semantic coherence
- **Trade-off**: May split long sentences or paragraphs

**Alternative Considered**: Semantic chunking
- More intelligent splitting
- Higher computational cost
- More complex implementation

### 4. Background Processing

**Choice**: FastAPI BackgroundTasks

**Rationale**:
- **Simplicity**: Built into FastAPI, no external dependencies
- **Adequate**: Sufficient for moderate workloads
- **Trade-off**: Jobs lost on server restart, no distributed processing

**Alternative Considered**: Celery + Redis
- Better for production at scale
- Job persistence
- More complex setup

### 5. Anti-Hallucination Strategy

**Multi-layered approach**:

1. **Prompt Engineering**: Explicit instructions to only use provided context
2. **Citation Extraction**: Parse chunk IDs from generated text
3. **Self-Check**: Analyze answer for unsupported claims
4. **Confidence Scoring**: Based on source quality and coverage

**Rationale**:
- **Defense in depth**: Multiple checks reduce hallucination risk
- **Transparency**: Citations allow users to verify
- **Trade-off**: May be overly conservative, rejecting valid answers

### 6. Rate Limiting

**Choice**: Simple in-memory rate limiter

**Rationale**:
- **Simplicity**: No external dependencies
- **Adequate**: Sufficient for single-instance deployments
- **Trade-off**: Doesn't work across multiple instances

**Alternative Considered**: Redis-based rate limiting
- Works across instances
- More complex setup

### 7. Logging

**Choice**: Structured JSON logging

**Rationale**:
- **Machine-readable**: Easy to parse and analyze
- **Context**: Request/job IDs for tracing
- **Production-ready**: Compatible with log aggregation tools

## Trade-offs

### Scalability

**Current Design**: Single-instance, in-memory processing
- **Pros**: Simple, fast for moderate workloads
- **Cons**: Limited horizontal scaling

**Future Improvements**:
- Distributed job queue (Celery/RQ)
- Shared vector store (pgvector)
- Load balancing

### Reliability

**Current Design**: Best-effort with error handling
- **Pros**: Graceful degradation
- **Cons**: Jobs lost on restart

**Future Improvements**:
- Job persistence (database)
- Retry mechanisms
- Dead letter queue

### Cost Optimization

**Current Design**: Configurable providers
- **Pros**: Users can choose cost/quality trade-off
- **Cons**: Requires manual configuration

**Future Improvements**:
- Automatic provider selection
- Caching of embeddings
- Batch processing

## Security Considerations

1. **Domain Allowlist**: Prevents crawling unauthorized domains
2. **Rate Limiting**: Prevents abuse
3. **Input Validation**: Pydantic schemas validate all inputs
4. **Error Handling**: No sensitive information in error messages

## Performance Characteristics

- **Ingestion**: ~1-2 seconds per page (fetch + clean + embed)
- **Query**: ~500ms-2s (embed + search + generate)
- **Memory**: ~100MB base + ~1MB per 1000 chunks

## Limitations

1. **Single-instance**: Not designed for distributed deployment
2. **In-memory index**: Limited by available RAM
3. **No incremental updates**: Must re-ingest to update content
4. **Basic deduplication**: Simple hash-based, may miss near-duplicates

## Future Enhancements

1. **Streaming responses**: Server-Sent Events for /ask
2. **Metrics endpoint**: Prometheus-style metrics
3. **Content quality scoring**: Reject low-quality pages
4. **Multi-language support**: Language detection and per-language strategies
5. **Incremental indexing**: Update existing indices
6. **Webhook notifications**: Notify on job completion

## Conclusion

This design prioritizes simplicity and correctness over scale. It's suitable for:
- Small to medium workloads
- Single-tenant deployments
- Research and development
- Production with moderate traffic

For larger scale, consider the alternatives mentioned above.

