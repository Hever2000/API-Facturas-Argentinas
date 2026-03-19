# FacturaAI

API para procesamiento de facturas argentinas utilizando OCR e IA. Extrae automáticamente datos estructurados de comprobantes y receipts.

## Características

- **OCR**: Extrae texto de imágenes de facturas usando PaddleOCR-VL
- **Extracción con IA**: Analiza datos estructurados usando Groq (Llama 3.3)
- **Formatos de exportación**: JSON y texto plano legible
- **Sistema de Feedback**: Corrige errores y mejora la IA progresivamente
- **Exportación de Dataset**: Genera datos para fine-tuning del modelo
- **API REST**: Interfaz basada en FastAPI
- **Docker**: Listo para despliegue en producción

## Campos de Factura Soportados

- Número de factura, fecha de emisión, fecha de vencimiento
- Información del vendedor (nombre, CUIT, dirección, condición de IVA)
- Información del cliente (nombre, CUIT, dirección)
- Ítems de la línea (descripción, cantidad, precio, importe)
- Totales financieros (subtotal, impuestos, total)
- Condiciones de pago y tipo de factura

## Stack

- **Framework**: FastAPI
- **OCR**: PaddleOCR-VL (remote) with EasyOCR fallback
- **LLM**: Groq (Llama 3.3)
- **Language**: Python 3.12

## Project Structure

```
├── src/
│   ├── api/
│   │   └── main.py          # FastAPI endpoints
│   ├── core/
│   │   ├── ocr.py           # OCR & LLM logic
│   │   └── feedback.py      # Feedback system
│   ├── models/
│   │   └── invoice.py       # Pydantic models
│   └── utils/
│       └── config.py        # Settings
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_api.py          # API tests
├── .github/workflows/        # CI/CD pipelines
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

```bash
curl "http://localhost:8000/v1/jobs/{job_id}"
```

### GET /v1/jobs/{job_id}/export
Export processed data as JSON or TXT.

```bash
# JSON (default)
curl "http://localhost:8000/v1/jobs/{job_id}/export"

# Plain text
curl "http://localhost:8000/v1/jobs/{job_id}/export?format=txt"
```

### GET /v1/jobs/{job_id}/text
Get invoice as formatted plain text.

```bash
curl "http://localhost:8000/v1/jobs/{job_id}/text"
```

### POST /v1/jobs/{job_id}/feedback
Submit correction feedback to improve future extractions.

```bash
curl -X POST "http://localhost:8000/v1/jobs/{job_id}/feedback" \
  -H "Content-Type: application/json" \
  -d '{"field": "vendedor_cuit", "correct_value": "30-12345678-9"}'
```

### GET /v1/training-data/export
Export feedback corrections as JSONL for model fine-tuning.

```bash
curl -O "http://localhost:8000/v1/training-data/export"
```

### GET /v1/feedback/stats
Get feedback correction statistics.

```bash
curl "http://localhost:8000/v1/feedback/stats"
```

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
```
