# NexTraction Web RAG Pipeline

A production-ready Web-based Retrieval-Augmented Generation (RAG) pipeline for extracting high-signal insights from public online sources. This FastAPI microservice fetches, processes, and indexes web content, then answers user questions with evidence-backed responses, proper citations, and safe refusal when information is insufficient.

## Features

- 🌐 **Web Crawling**: Bounded crawling with domain allowlist, max pages, and depth control
- 🧹 **Content Cleaning**: HTML to clean text conversion with boilerplate removal
- 📦 **Smart Chunking**: Text chunking with metadata preservation
- 🔍 **Vector Search**: FAISS-based vector indexing for semantic search
- 🤖 **Grounded Generation**: LLM-powered answers with mandatory citations
- 🛡️ **Anti-Hallucination**: Self-check mechanisms to prevent unsupported claims
- ⚡ **Background Processing**: Non-blocking ingestion with job status tracking
- 📊 **Structured Logging**: JSON-formatted logs with request/job context
- 🚀 **Docker Ready**: One-command deployment with docker-compose

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional)
- OpenAI API key (or configure for Gemini/local embeddings)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Nextraction
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run manually
docker build -t nextraction .
docker run -p 8000:8000 --env-file .env nextraction
```

## API Endpoints

### POST /ingest

Start an ingestion job to crawl and index web pages.

**Request:**
```json
{
  "seed_urls": ["https://example.com/page1", "https://example.com/page2"],
  "domain_allowlist": ["example.com"],
  "max_pages": 20,
  "max_depth": 2,
  "user_notes": "Optional tag for this ingestion"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "accepted_pages": 2
}
```

### GET /status/{job_id}

Check the status of an ingestion job.

**Response:**
```json
{
  "state": "done",
  "pages_fetched": 15,
  "pages_indexed": 42,
  "error": null
}
```

States: `queued`, `running`, `done`, `failed`

### POST /ask

Ask a question against an indexed job.

**Request:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What are the main features of this product?"
}
```

**Response:**
```json
{
  "answer": "Based on the indexed content, the main features include...",
  "citations": [
    {
      "url": "https://example.com/page1",
      "title": "Product Overview",
      "chunkid": "abc123...",
      "quote": "The product includes feature A, feature B...",
      "score": 0.85
    }
  ],
  "confidence": "high",
  "groundingnotes": "Answer is well-supported by 3 high-quality sources"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Example Usage

### Using curl

```bash
# 1. Start ingestion
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 10,
    "max_depth": 1
  }'

# 2. Check status (replace JOB_ID)
curl "http://localhost:8000/status/JOB_ID"

# 3. Ask a question (replace JOB_ID)
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_ID",
    "question": "What is this website about?"
  }'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Start ingestion
response = requests.post(f"{BASE_URL}/ingest", json={
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 10,
    "max_depth": 1
})
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"{BASE_URL}/status/{job_id}").json()
print(f"Status: {status['state']}")

# Ask question
answer = requests.post(f"{BASE_URL}/ask", json={
    "job_id": job_id,
    "question": "What is this website about?"
}).json()
print(f"Answer: {answer['answer']}")
print(f"Citations: {len(answer['citations'])}")
```

## Configuration

Key environment variables (see `.env.example` for full list):

- `OPENAI_API_KEY`: Your OpenAI API key
- `EMBEDDING_PROVIDER`: `openai`, `gemini`, or `local`
- `LLM_PROVIDER`: `openai` or `gemini`
- `CHUNK_SIZE`: Text chunk size (default: 500)
- `TOP_K`: Number of chunks to retrieve (default: 5)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FORMAT`: `json` or `text` (default: json)

## Project Structure

```
Nextraction/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic models
│   ├── routers/             # API route handlers
│   │   ├── ingest.py
│   │   ├── status.py
│   │   ├── ask.py
│   │   └── health.py
│   ├── services/            # Business logic
│   │   ├── fetcher.py       # Web crawling
│   │   ├── cleaner.py       # HTML cleaning & chunking
│   │   ├── embedder.py      # Embedding generation
│   │   ├── vector_store.py  # Vector indexing
│   │   ├── generator.py     # Grounded generation
│   │   └── job_manager.py   # Job orchestration
│   ├── middleware/          # Custom middleware
│   │   └── rate_limit.py
│   └── utils/               # Utilities
│       └── logger.py
├── tests/                   # Unit tests
├── data/                    # Data storage (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Design Decisions

See [DESIGN.md](DESIGN.md) for detailed design notes and trade-offs.

## Evaluation

See [evaluation.py](evaluation.py) for example questions and citation quality assessment.

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

