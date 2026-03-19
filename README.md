# Backend API

OCR + LLM invoice processing API for Argentine invoices.

## Stack

- **Framework**: FastAPI
- **OCR**: PaddleOCR-VL (remote) with EasyOCR fallback
- **LLM**: Groq (Llama 3.3)
- **Language**: Python 3.12

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── main.py          # FastAPI endpoints
│   ├── core/
│   │   └── ocr.py           # OCR & LLM logic
│   ├── models/
│   │   └── invoice.py       # Pydantic models
│   └── utils/
│       └── config.py        # Settings
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_api.py          # API tests
├── scripts/
│   └── lint-fix.sh          # Linting script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## Getting Started

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.api.main:app --reload --port 8000
```

### Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# PaddleOCR-VL (remote API)
PADDLE_VL_API_URL=https://c6vceb62c4n8zfaf.aistudio-app.com/layout-parsing
PADDLE_VL_TOKEN=your_token

# Optional
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## API Endpoints

### POST /v1/process
Upload and process an invoice image.

```bash
curl -X POST "http://localhost:8000/v1/process" \
  -F "file=@factura.pdf"
```

### GET /v1/jobs/{job_id}
Get job status and results.

### GET /v1/jobs/{job_id}/export
Export processed data as JSON.

### GET /health
Health check endpoint.

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src --cov-report=html
```

## Linting

```bash
# Auto-fix
ruff check --fix .

# Format
black --line-length=100 .
isort --profile=black .
```
