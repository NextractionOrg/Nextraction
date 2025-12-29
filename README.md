# NexTraction - Web-based RAG Pipeline

A FastAPI microservice for extracting high-signal insights from public online sources using Retrieval-Augmented Generation (RAG). This service fetches, processes, and indexes web content, then answers user questions with evidence-backed responses, proper citations, and safe refusal when information is insufficient.

## 🎯 Features

- **Web Crawling**: Bounded web page fetching with domain restrictions and depth limits
- **Content Processing**: HTML cleaning, boilerplate removal, and intelligent chunking
- **Vector Indexing**: FAISS-based semantic search with persistent storage
- **Grounded Generation**: LLM-powered answers strictly based on retrieved evidence
- **Anti-Hallucination**: Mandatory citations, self-check mechanisms, and confidence scoring
- **Authentication**: JWT-based user authentication and authorization
- **Background Processing**: Non-blocking ingestion with job status tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NextractionOrg/Nextraction.git
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

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Start the server**
   ```bash
   python run.py
   # Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t nextraction-api .
docker run -p 8000:8000 --env-file .env nextraction-api
```

## 📚 API Endpoints

### POST /ingest
Start an ingestion job to crawl and index web pages.

**Request:**
```json
{
  "seed_urls": ["https://example.com/page1", "https://example.com/page2"],
  "domain_allowlist": ["example.com"],
  "max_pages": 20,
  "max_depth": 2,
  "user_notes": "optional text tag"
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "accepted_pages": 2
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 10,
    "max_depth": 1
  }'
```

### GET /status/{job_id}
Get the status of an ingestion job.

**Response:**
```json
{
  "state": "queued|running|done|failed",
  "pages_fetched": 5,
  "pages_indexed": 5,
  "error": null
}
```

**Example:**
```bash
curl "http://localhost:8000/status/{job_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /ask
Ask a question against an indexed job.

**Request:**
```json
{
  "job_id": "uuid-here",
  "question": "What is the main topic of this website?"
}
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "citations": [
    {
      "url": "https://example.com/page1",
      "title": "Page Title",
      "chunkid": "abc123",
      "quote": "Short excerpt from the source...",
      "score": 0.85
    }
  ],
  "confidence": "high|medium|low",
  "groundingnotes": "Answer is well-supported by 3 high-quality sources"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "uuid-here",
    "question": "What are the key features?"
  }'
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl "http://localhost:8000/health"
```

## 🔐 Authentication

The API uses JWT-based authentication. You need to register and login first:

### Register
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword"
```

Use the returned `access_token` in subsequent requests:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" "http://localhost:8000/..."
```

## ⚙️ Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `OPENAI_API_KEY`: OpenAI API key for embeddings/LLM (optional if using local)
- `GEMINI_API_KEY`: Google Gemini API key (alternative to OpenAI)
- `EMBEDDING_PROVIDER`: `openai`, `gemini`, or `local` (default: `openai`)
- `LLM_PROVIDER`: `openai` or `gemini` (default: `openai`)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (required)
- `PASSWORD_SALT`: Salt for password hashing (auto-generated if not provided)

See `.env.example` for complete list.

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Evaluation Script
Test the pipeline with example questions:
```bash
python scripts/evaluation.py
```

## 📖 Documentation

- **API Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)
- **Project Structure**: See `STRUCTURE.md` for complete project organization
- **Documentation Index**: See `docs/README.md` for all available documentation
- **Design Document**: See `docs/DESIGN.md` for architecture and trade-offs
- **Guides**: Check `docs/guides/` for detailed usage guides
- **Deployment Guides**: Check `docs/deployment/` for deployment instructions
- **Requirements Audit**: See `docs/analysis/REQUIREMENTS_AUDIT.md` for compliance verification

## 🏗️ Architecture

```
User Request
    ↓
API Endpoint (FastAPI)
    ↓
Background Job Manager
    ↓
┌─────────────────────────────────┐
│ 1. Fetch (Web Crawler)          │
│ 2. Clean (HTML → Text)          │
│ 3. Chunk (Text Segmentation)    │
│ 4. Embed (Vector Generation)    │
│ 5. Index (FAISS Storage)       │
└─────────────────────────────────┘
    ↓
Query Processing
    ↓
┌─────────────────────────────────┐
│ 1. Embed Query                  │
│ 2. Vector Search (Top-K)        │
│ 3. Generate Answer (LLM)        │
│ 4. Extract Citations            │
│ 5. Self-Check & Confidence      │
└─────────────────────────────────┘
    ↓
Response with Citations
```

## 🔒 Security Features

- **Domain Allowlist**: Prevents crawling unauthorized domains
- **Rate Limiting**: Prevents API abuse (60 requests/minute default)
- **Input Validation**: Pydantic schemas validate all inputs
- **JWT Authentication**: Secure token-based authentication
- **Error Handling**: No sensitive information in error messages

## 📊 Performance

- **Ingestion**: ~1-2 seconds per page (fetch + clean + embed)
- **Query**: ~500ms-2s (embed + search + generate)
- **Memory**: ~100MB base + ~1MB per 1000 chunks

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Vector Store**: FAISS
- **Embeddings**: OpenAI, Gemini, or sentence-transformers (local)
- **LLM**: OpenAI GPT-4o-mini or Gemini Pro
- **HTML Processing**: BeautifulSoup4
- **HTTP Client**: httpx
- **Authentication**: PyJWT

## 📝 License

This project is part of a technical evaluation. See repository for license details.

## 🤝 Contributing

This is an evaluation project. For questions or issues, please open an issue on GitHub.

## 📧 Contact

For questions about this implementation, see the design document or open an issue.

---

**Note**: This service is designed for small to medium workloads. For production at scale, consider the alternatives mentioned in `docs/DESIGN.md`.

