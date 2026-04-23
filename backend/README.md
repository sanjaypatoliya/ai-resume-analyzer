# Backend — FastAPI

Python 3.12 REST API using FastAPI. Orchestrates the full resume analysis pipeline: S3 upload → Textract OCR → Claude AI analysis → DynamoDB storage.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/upload` | Get presigned S3 URL to upload PDF |
| POST | `/api/v1/analyze` | Analyze resume against job description |
| GET | `/api/v1/history` | List recent analysis results |
| GET | `/api/v1/history/{id}` | Get a single result by ID |
| DELETE | `/api/v1/history/{id}` | Delete a result by ID |

### POST `/api/v1/upload`
**Request:**
```json
{ "file_name": "resume.pdf", "content_type": "application/pdf" }
```
**Response:**
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "s3_key": "uploads/uuid/resume.pdf",
  "expires_in": 300
}
```

### POST `/api/v1/analyze`
**Request:**
```json
{
  "s3_key": "uploads/uuid/resume.pdf",
  "job_description": "We are looking for a Senior Python Developer..."
}
```
**Response:**
```json
{
  "id": "uuid",
  "overall_score": 78,
  "categories": [
    { "name": "Skills Match", "score": 85, "rationale": "Strong Python and AWS skills" },
    { "name": "Experience Level", "score": 70, "rationale": "5 years matches requirement" },
    { "name": "Education", "score": 90, "rationale": "Relevant CS degree" },
    { "name": "Keywords", "score": 75, "rationale": "Most keywords present" },
    { "name": "ATS Formatting", "score": 65, "rationale": "Some formatting improvements needed" }
  ],
  "skills": ["Python", "FastAPI", "AWS", "Docker"],
  "experience": [{ "title": "Senior Engineer", "company": "Acme", "duration": "2021-2024" }],
  "education": [{ "degree": "BS Computer Science", "institution": "State University", "year": "2018" }],
  "suggestions": [
    "Add quantifiable achievements to your experience section",
    "Include AWS certification names explicitly"
  ],
  "created_at": "2026-04-03T10:00:00Z",
  "file_name": "resume.pdf"
}
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point, CORS config
│   ├── config.py                # Pydantic Settings (env vars)
│   ├── models/
│   │   ├── requests.py          # UploadRequest, AnalyzeRequest
│   │   └── responses.py         # UploadResponse, AnalysisResult, HistoryResponse
│   ├── routers/
│   │   ├── upload.py            # POST /api/v1/upload
│   │   ├── analyze.py           # POST /api/v1/analyze
│   │   └── history.py           # GET/DELETE /api/v1/history
│   └── services/
│       ├── s3_service.py        # Presigned URLs, PDF storage
│       ├── textract_service.py  # PDF text extraction
│       ├── bedrock_service.py   # Claude AI analysis
│       ├── dynamodb_service.py  # Results storage
│       └── analysis_service.py  # Orchestrates full pipeline
├── tests/
│   ├── conftest.py              # Shared fixtures (mock AWS, settings)
│   ├── models/                  # Request/response model tests
│   ├── services/                # Service logic tests
│   └── routers/                 # API endpoint tests
├── Dockerfile
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Local Setup

**Step 1 — Create virtual environment:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

> Run `source .venv/bin/activate` every time you open a new terminal.

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Create environment file:**
```bash
cp .env.example .env
```

**Step 4 — Start the API:**
```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `APP_ENV` | `development` or `production` | No (default: development) |
| `AWS_REGION` | AWS region | No (default: us-east-1) |
| `AWS_PROFILE` | Named AWS CLI profile | One of these |
| `AWS_ACCESS_KEY_ID` | AWS access key | One of these |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | One of these |
| `S3_BUCKET` | S3 bucket name | Yes |
| `S3_PRESIGNED_URL_EXPIRY` | Presigned URL TTL in seconds | No (default: 300) |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes |
| `ANTHROPIC_MODEL_ID` | Claude model ID | No (default: claude-sonnet-4-6) |
| `DYNAMODB_TABLE` | DynamoDB table name | No (default: resume-analyzer-results) |

---

## Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests with coverage
pytest

# Run specific folders
pytest tests/services/ -v
pytest tests/routers/ -v
pytest tests/models/ -v
```

Tests use `moto` to mock AWS — no real AWS credentials needed.

**Coverage:**
- Minimum threshold: **70%**
- HTML report: open `htmlcov/index.html` in browser


## Author

**Sanjay Patoliya**

- Email: sbpatoliya@gmail.com
- LinkedIn: https://linkedin.com/in/sanjaykumar-patoliya-b234a287/
- GitHub: https://github.com/sanjaypatoliya
- Portfolio: https://sanjaypatoliya.com
