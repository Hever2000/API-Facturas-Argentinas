# FacturaAI

API para procesamiento de facturas argentinas utilizando OCR e IA. Extrae automáticamente datos estructurados de comprobantes y receipts.

## Características

- **OCR**: Extrae texto de imágenes de facturas usando PaddleOCR-VL / EasyOCR
- **Extracción con IA**: Analiza datos estructurados usando Groq (Llama 3.3)
- **Autenticación**: JWT con access y refresh tokens
- **API Keys**: Gestión de claves API para acceso programático
- **Suscripciones**: Integración con Mercado Pago
- **Rate Limiting**: Control de uso por usuario
- **Feedback**: Sistema de corrección para mejorar la IA progresivamente
- **Exportación**: JSON y texto plano legible
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

- **Framework**: FastAPI (Python 3.11+)
- **OCR**: PaddleOCR-VL (remote) / EasyOCR (fallback)
- **LLM**: Groq (Llama 3.3)
- **Database**: PostgreSQL + SQLAlchemy (async)
- **Cache**: Redis
- **Auth**: JWT (python-jose)
- **Payments**: Mercado Pago

## Project Structure

```
facturaai/
├── src/
│   ├── api/
│   │   ├── main.py            # FastAPI app initialization
│   │   ├── deps.py             # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── auth.py         # Register, login, refresh, me
│   │       ├── apikeys.py      # API keys management
│   │       ├── jobs.py         # Invoice processing jobs
│   │       ├── subscriptions.py # Mercado Pago subscriptions
│   │       ├── webhooks.py     # Payment webhooks
│   │       └── rate_limit.py   # Rate limiting status
│   ├── core/
│   │   ├── config.py           # Settings
│   │   ├── ocr.py             # OCR processing
│   │   ├── security.py        # JWT utilities
│   │   └── feedback.py         # Feedback system
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── job.py              # Job model
│   │   ├── apikey.py           # API key model
│   │   └── invoice.py         # Invoice schema
│   ├── schemas/                # Pydantic schemas
│   ├── services/
│   │   ├── auth.py             # Auth logic
│   │   ├── apikey.py           # API key logic
│   │   ├── subscription.py     # Subscription logic
│   │   └── mercadopago.py      # Mercado Pago integration
│   └── db/
│       ├── session.py          # Database session
│       └── redis.py            # Redis client
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   └── test_api.py            # API tests
├── .github/workflows/          # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Getting Started

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

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
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your-secret-key-min-32-chars

# PaddleOCR-VL (remote API)
PADDLE_VL_API_URL=https://c6vceb62c4n8zfaf.aistudio-app.com/layout-parsing
PADDLE_VL_TOKEN=your_token

# Mercado Pago
MP_ACCESS_TOKEN=your_mp_access_token
MP_WEBHOOK_SECRET=your_webhook_secret

# Optional
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/register` | Register new user |
| POST | `/v1/auth/login` | Login (returns JWT) |
| POST | `/v1/auth/refresh` | Refresh access token |
| GET | `/v1/auth/me` | Get current user info |

### API Keys

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/apikeys` | Create API key |
| GET | `/v1/apikeys` | List user's API keys |
| GET | `/v1/apikeys/{id}` | Get API key details |
| PATCH | `/v1/apikeys/{id}` | Update API key |
| POST | `/v1/apikeys/{id}/rotate` | Rotate API key secret |
| DELETE | `/v1/apikeys/{id}` | Delete API key |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/jobs/process` | Upload and process invoice |
| GET | `/v1/jobs` | List user's jobs |
| GET | `/v1/jobs/{job_id}` | Get job status/result |
| GET | `/v1/jobs/{job_id}/export` | Export as JSON/TXT |
| GET | `/v1/jobs/{job_id}/text` | Get formatted text |
| POST | `/v1/jobs/{job_id}/feedback` | Submit correction |

### Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/subscriptions/plans` | Get available plans |
| POST | `/v1/subscriptions/subscribe` | Subscribe to plan |
| GET | `/v1/subscriptions/current` | Get current subscription |
| POST | `/v1/subscriptions/cancel` | Cancel subscription |
| POST | `/v1/subscriptions/pause` | Pause subscription |
| POST | `/v1/subscriptions/resume` | Resume subscription |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/rate-limit/status` | Get rate limit status |
| POST | `/v1/webhooks/mercadopago` | Mercado Pago webhook |
| GET | `/health` | Health check |

## Example Usage

### Login

```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Process Invoice

```bash
curl -X POST "http://localhost:8000/v1/jobs/process" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@factura.pdf"
```

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html
```

## Linting

```bash
# Auto-fix with ruff
ruff check --fix .

# Format with black
black --line-length=100 .

# Sort imports
isort --profile=black .

# Type checking
mypy src/ --ignore-missing-imports
```

## Deployment

### Render (Backend)

1. Connect GitHub repository to Render
2. Create a new Web Service
3. Use the following settings:
   - Build Command: (empty - using Dockerfile)
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string
   - `SECRET_KEY`: Your secret key (min 32 chars)
   - `GROQ_API_KEY`: Your Groq API key
   - `STORAGE_BACKEND`: `local` (or `r2` for Cloudflare R2)
5. Deploy from `main` branch

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key-min-32-chars
GROQ_API_KEY=your_groq_api_key

# Optional - Storage
STORAGE_BACKEND=local  # or "r2" for Cloudflare R2

# R2 Storage (only if STORAGE_BACKEND=r2)
R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=facturaai-storage

# Optional - OCR
PADDLE_VL_API_URL=https://c6vceb62c4n8zfaf.aistudio-app.com/layout-parsing
PADDLE_VL_TOKEN=your_token

# Optional - Mercado Pago
MP_ACCESS_TOKEN=your_mp_access_token
MP_WEBHOOK_SECRET=your_webhook_secret
```

### Vercel (Frontend)

1. Deploy Next.js frontend
2. Configure environment variables
3. Add backend URL to CORS origins

## License

MIT
