# ZenithOCR

OCR + LLM invoice processing API for Argentine invoices.

## Features

- **OCR**: Extract text from invoice images using EasyOCR
- **LLM Extraction**: Parse structured data using Groq (Llama 3.3)
- **Export**: Download processed data as JSON
- **REST API**: FastAPI-based RESTful interface
- **Docker**: Ready for production deployment

## Supported Invoice Fields

- Invoice number, date, due date
- Vendor info (name, CUIT, address, IVA condition)
- Customer info (name, CUIT, address)
- Line items (description, quantity, price, amount)
- Financial totals (subtotal, tax, total)
- Payment conditions and invoice type

## Requirements

- Python 3.12+
- Groq API Key ([get one here](https://console.groq.com/))

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/zenith-ocr.git
cd zenith-ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
uvicorn src.api.main:app --reload
```

### Docker

```bash
# Build and run with Docker
docker-compose up --build

# Or build manually
docker build -t zenith-ocr .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key zenith-ocr
```

## Usage

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/process` | POST | Upload invoice for processing |
| `/v1/jobs/{job_id}` | GET | Get job status and results |
| `/v1/jobs/{job_id}/export` | GET | Export as JSON file |
| `/health` | GET | Health check |

### Example: Process Invoice

```bash
# Upload invoice
curl -X POST -F "file=@invoice.png" http://localhost:8000/v1/process

# Response:
# {"job_id": "abc-123", "status": "PROCESSED"}

# Get results
curl http://localhost:8000/v1/jobs/abc-123

# Export JSON
curl http://localhost:8000/v1/jobs/abc-123/export -o invoice.json
```

### Python Client

```python
import requests

# Upload
with open("invoice.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/v1/process",
        files={"file": f}
    )
job_id = response.json()["job_id"]

# Get results
result = requests.get(f"http://localhost:8000/v1/jobs/{job_id}").json()
print(result["extracted_data"])
```

## Project Structure

```
zenith-ocr/
├── src/
│   ├── api/          # FastAPI endpoints
│   ├── core/        # OCR & LLM logic
│   ├── models/      # Pydantic models
│   └── utils/       # Utilities
├── tests/           # Test files
├── docker/          # Docker configs
├── docs/            # Documentation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `OCR_LANGUAGES` | OCR languages | `en,es` |
| `LOG_LEVEL` | Logging level | `INFO` |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
