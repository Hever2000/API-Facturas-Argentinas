# AGENTS.md - ZenithOCR Developer Guide

This file provides guidance for AI agents working on the ZenithOCR project.

## Project Overview

ZenithOCR is a microservices-based OCR document processing system with:
- FastAPI REST API for ingestion
- Celery workers for async processing (OCR, LLM, Export)
- PostgreSQL for metadata/jobs
- MinIO/S3 for object storage
- Redis as message broker

## Project Structure

```
zenith-ocr/
├── services/
│   ├── api/              # FastAPI REST API
│   ├── ocr-worker/       # PaddleOCR processing
│   ├── llm-worker/       # LLM parsing/structuring
│   ├── export-worker/    # Export to JSON/CSV/Excel
│   └── hitl-service/     # Human-in-the-loop review
├── shared/
│   ├── models/           # Pydantic schemas (shared across services)
│   ├── messaging/        # Celery configuration
│   └── storage/          # S3/MinIO utilities
└── docker/               # Docker configurations
```

## Build/Lint/Test Commands

### Running Individual Services

```bash
# API Service
cd services/api
pip install -r requirements.txt
uvicorn services.api.main:app --reload --port 8000

# OCR Worker (requires PaddlePaddle)
cd services/ocr-worker
pip install -r requirements.txt
celery -A shared.messaging.celery_app worker -Q ocr_queue --loglevel=info

# LLM Worker
cd services/llm-worker
pip install -r requirements.txt
celery -A shared.messaging.celery_app worker -Q llm_queue --loglevel=info

# Export Worker
cd services/export-worker
pip install -r requirements.txt
celery -A shared.messaging.celery_app worker -Q export_queue --loglevel=info
```

### Docker Compose (Full Stack)

```bash
# Build and start all services
docker-compose up --build

# Scale specific workers
docker-compose up --scale ocr-worker=3
```

### Testing

```bash
# Run tests (if pytest configured)
pytest tests/                    # Run all tests
pytest tests/test_api.py         # Run specific test file
pytest tests/test_api.py::test_job_status  # Run single test
pytest -k "test_job"             # Run tests matching pattern
pytest --tb=short                # Shorter traceback output

# With coverage
pytest --cov=services --cov-report=html
```

### Linting

```bash
# Flake8
flake8 services/ --max-line-length=100 --ignore=E501,W503

# Black formatting
black services/ --line-length=100

# isort import sorting
isort services/ --profile=black

# mypy type checking
mypy services/ --ignore-missing-imports --strict
```

## Code Style Guidelines

### General Principles

- Write clean, readable, and maintainable code
- Follow the DRY (Don't Repeat Yourself) principle
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)
- Add type hints to all function signatures
- Document complex business logic with docstrings

### Imports

```python
# Standard library first
import os
import sys
from typing import List, Optional, Dict, Any
from enum import Enum

# Third-party imports
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, field_validator

# Local application imports
from shared.models.invoice import JobStatus, InvoiceData
from shared.messaging.celery_app import celery_app
```

### Formatting

- Line length: 100 characters max
- Use 4 spaces for indentation (no tabs)
- Use Black for automatic formatting
- Use isort for import sorting
- One blank line between top-level definitions

### Type Hints

Always use type hints for function parameters and return values:

```python
# Good
def process_document(job_id: str, file_path: str) -> Dict[str, Any]:
    pass

def get_job_status(job_id: str) -> Optional[JobStatus]:
    pass

# Avoid
def process_document(job_id, file_path):
    pass
```

### Naming Conventions

- **Variables/Functions**: `snake_case` (e.g., `job_id`, `process_ocr`)
- **Classes**: `PascalCase` (e.g., `InvoiceData`, `JobStatus`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)
- **Private members**: Prefix with underscore (e.g., `_internal_method`)

### Error Handling

Always handle exceptions properly:

```python
# Use try/except for recoverable errors
try:
    result = ocr_engine.ocr(file_path)
except Exception as e:
    logger.error(f"OCR failed for job {job_id}: {str(e)}")
    raise

# Use custom exceptions for domain-specific errors
class OCRProcessingError(Exception):
    pass

# Return appropriate HTTP status codes in FastAPI
from fastapi import HTTPException

if not job:
    raise HTTPException(status_code=404, detail="Job not found")
```

### Pydantic Models

Follow Pydantic v2 conventions:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class InvoiceData(BaseModel):
    invoice_number: str
    vendor_name: str
    tax_id: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    
    @field_validator("invoice_number")
    @classmethod
    def validate_invoice_number(cls, v: str) -> str:
        if not v:
            raise ValueError("Invoice number cannot be empty")
        return v.upper()
```

### Celery Tasks

```python
from shared.messaging.celery_app import celery_app

@celery_app.task(name="services.ocr_worker.tasks.process_ocr", 
                 bind=True,
                 max_retries=3,
                 default_retry_delay=60)
def process_ocr(self, job_id: str, file_path: str) -> Dict[str, Any]:
    try:
        # Task logic here
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        raise self.retry(exc=e)
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

def process_ocr(job_id: str, file_path: str):
    logger.info(f"Starting OCR processing for job {job_id}")
    # ... processing ...
    logger.info(f"OCR completed for job {job_id}", extra={"job_id": job_id})
```

### Database Operations

Use SQLAlchemy or asyncpg with proper connection handling:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### API Endpoints

Follow RESTful conventions:

```python
@app.post("/v1/process", status_code=202)  # 202 Accepted for async
async def create_process_job(file: UploadFile = File(...)):
    """Process a document asynchronously."""
    pass

@app.get("/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job."""
    pass
```

## Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/zenith_ocr

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_USER=minioadmin
STORAGE_PASSWORD=minioadmin
STORAGE_BUCKET=zenith-ocr

# LLM (if using OpenAI)
OPENAI_API_KEY=sk-...
```

## Common Patterns

### File Uploads

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save to temp or upload to S3
    contents = await file.read()
    # Process...
    return {"filename": file.filename}
```

### Async Task Chaining

```python
# After OCR completes, chain to LLM task
celery_app.send_task("services.llm_worker.tasks.process_llm", 
                     args=[job_id, raw_text])

# After LLM completes, chain to export or HITL
if confidence_score < 0.85:
    celery_app.send_task("services.hitl_service.tasks.queue_review", 
                         args=[job_id])
else:
    celery_app.send_task("services.export_worker.tasks.export_data", 
                         args=[job_id, output_format])
```

## Docker Development

```bash
# Build image
docker build -t zenith-ocr-api -f services/api/Dockerfile .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=... zenith-ocr-api

# View logs
docker logs -f container_id

# Exec into container
docker exec -it container_id /bin/bash
```

## Best Practices

1. **Never commit secrets** - Use environment variables or .env files (add .env to .gitignore)
2. **Use dependency injection** - Pass dependencies as parameters, don't import globally
3. **Write tests first** - TDD approach for new features
4. **Keep config separate** - No hardcoded values, use config files
5. **Handle timeouts** - Set appropriate timeouts for external API calls
6. **Log appropriately** - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
7. **Graceful shutdown** - Handle SIGTERM in workers for clean shutdowns

## Git Workflow & Branch Protection

### Branch Strategy

- **main**: Production-ready code (protected)
- **develop**: Development branch for integration
- **feature/***: Feature branches for new functionality
- **fix/***: Bug fix branches

### Branch Protection Rules

The `main` branch is protected. Direct pushes are **not allowed**. All changes must go through Pull Requests.

**How to contribute:**

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

3. Push and create a Pull Request:
   ```bash
   git push -u origin feature/my-new-feature
   ```

4. Open a Pull Request on GitHub
5. Wait for CI/CD checks to pass
6. Request review from maintainers
7. Merge after approval

### CI/CD Requirements

Before merging, all checks must pass:
- ✅ Tests (pytest)
- ✅ Linting (ruff, black, isort)
- ✅ Type checking (mypy)
- ✅ Docker build

### Prohibited Actions

- ❌ Direct push to `main`
- ❌ Commit secrets or API keys
- ❌ Disable CI/CD checks
