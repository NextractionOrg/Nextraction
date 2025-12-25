# Quick Start Guide

Get up and running with NexTraction Web RAG in 5 minutes!

## Prerequisites

- Python 3.11+
- OpenAI API key (or configure for Gemini/local)

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example env file
cp env.example.txt .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Start the Server

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload

# Option 2: Using the run script
python run.py
```

The API will be available at `http://localhost:8000`

## Step 4: Test the API

### Using the Interactive Docs

Visit `http://localhost:8000/docs` for interactive API documentation.

### Using curl

```bash
# 1. Start an ingestion job
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 5,
    "max_depth": 1
  }'

# Save the job_id from the response, then:

# 2. Check job status (replace YOUR_JOB_ID)
curl "http://localhost:8000/status/YOUR_JOB_ID"

# 3. Ask a question (replace YOUR_JOB_ID)
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "YOUR_JOB_ID",
    "question": "What is this website about?"
  }'
```

### Using Python

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Start ingestion
response = requests.post(f"{BASE_URL}/ingest", json={
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 5,
    "max_depth": 1
})
job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Wait for completion
while True:
    status = requests.get(f"{BASE_URL}/status/{job_id}").json()
    print(f"Status: {status['state']}")
    if status['state'] in ['done', 'failed']:
        break
    time.sleep(2)

# Ask a question
if status['state'] == 'done':
    answer = requests.post(f"{BASE_URL}/ask", json={
        "job_id": job_id,
        "question": "What is this website about?"
    }).json()
    print(f"\nAnswer: {answer['answer']}")
    print(f"\nCitations: {len(answer['citations'])}")
```

## Step 5: Run Evaluation

```bash
python evaluation.py
```

## Troubleshooting

### "No embedding provider available"

Make sure you've installed the required packages:
- For OpenAI: `pip install openai`
- For Gemini: `pip install google-generativeai`
- For local: `pip install sentence-transformers`

### "FAISS not available"

Install FAISS:
```bash
pip install faiss-cpu
```

### Port already in use

Change the port:
```bash
uvicorn app.main:app --port 8001
```

## Next Steps

- Read the [README.md](README.md) for detailed documentation
- Check [DESIGN.md](DESIGN.md) for architecture details
- Customize configuration in `.env`

