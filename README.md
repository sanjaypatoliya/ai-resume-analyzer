# AI Resume Analyzer

Upload a resume PDF and a job description — AWS Textract extracts the text, Claude AI scores the match and suggests specific improvements.

---

## Architecture

```
Browser
  │
  ▼
CloudFront (HTTPS)
  ├── /* ──────────────► S3 (React static files)
  └── /api/v1/* ───────► ALB
                           │
                           ▼
                      ECS Fargate (FastAPI)
                           │
                           ▼
                      S3 — fetch uploaded PDF
                           │
                           ▼
                      Textract — extract text (OCR)
                           │
                           ▼
                      Anthropic Claude AI — score + suggestions
                           │
                           ▼
                      DynamoDB — save result
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + TailwindCSS |
| Backend | FastAPI (Python 3.12) |
| AI | Anthropic Claude (claude-sonnet-4-6) |
| OCR | AWS Textract |
| Storage | Amazon S3 + DynamoDB |
| Hosting | ECS Fargate + ALB + CloudFront |
| IaC | AWS CDK (Python) |

---

## AWS Services Used

| Service | Purpose |
|---|---|
| Amazon ECS Fargate | Serverless container hosting for FastAPI |
| Application Load Balancer | Routes traffic to ECS tasks |
| Amazon CloudFront | CDN + HTTPS termination |
| Amazon S3 | Resume PDF storage + React static hosting |
| Amazon DynamoDB | Analysis results and history |
| AWS Textract | Extract text from resume PDFs |
| AWS SSM Parameter Store | Secure API key storage |
| Amazon ECR | Docker image registry |
| Amazon VPC + NAT Gateway | Private network with internet access |
| AWS CDK (Python) | Infrastructure as Code |

---

## Features

- Upload resume PDF via drag-and-drop
- Paste any job description
- AI scores resume match (0–100) across 5 categories
- Extracted skills, experience, and education
- Specific improvement suggestions
- Analysis history with View and Delete per record

---

## Project Structure

```
resume-parser/
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── infrastructure/   # AWS CDK Python stacks
├── Makefile          # Deploy and test commands
└── docker-compose.yml
```

## Sub-READMEs

- [Backend →](backend/README.md) — API endpoints, local setup, testing
- [Frontend →](frontend/README.md) — Pages, local setup, testing
- [Infrastructure →](infrastructure/README.md) — AWS architecture, CDK stacks, deploy guide

---

## Quick Start

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.12+ |
| Node.js | 18+ |
| AWS CLI | v2 |
| AWS CDK CLI | latest (`npm install -g aws-cdk`) |

### Run Locally

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your values
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

App runs at **http://localhost:5173**

### Deploy to AWS

```bash
make deploy
```

This runs all tests first — deployment stops if any test fails.

---

## Makefile Commands

| Command | Description |
|---|---|
| `make test` | Run backend + frontend tests |
| `make test-backend` | Run backend tests only |
| `make test-frontend` | Run frontend tests only |
| `make build` | Build frontend for production |
| `make deploy` | Test → Build → Deploy to AWS |
| `make destroy` | Destroy all AWS stacks |

---

## License

MIT


## Author

**Sanjay Patoliya**

- Email: sbpatoliya@gmail.com
- LinkedIn: https://linkedin.com/in/sanjaykumar-patoliya-b234a287/
- GitHub: https://github.com/sanjaypatoliya
- Portfolio: https://sanjaypatoliya.com
