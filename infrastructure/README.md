# Infrastructure — AWS CDK (Python)

All AWS infrastructure defined as code using AWS CDK (Python).

---

## Architecture

```
CloudFront Distribution
  ├── Default behaviour  ──► S3 Bucket (React static files)
  └── /api/v1/*          ──► Application Load Balancer
                                   │
                              ECS Fargate (FastAPI)
                              Private Subnet + NAT Gateway
                                   │
                              S3 Bucket — fetch uploaded PDF
                                   │
                              AWS Textract — extract text (OCR)
                                   │
                              Anthropic Claude AI — score + suggestions
                              (via NAT Gateway → api.anthropic.com)
                                   │
                              DynamoDB — save analysis result
                              SSM Parameter Store — Anthropic API key
```

---

## CDK Stacks

| Stack | Description |
|---|---|
| `ResumeParser-Storage-dev` | S3 bucket for resume PDFs |
| `ResumeParser-Database-dev` | DynamoDB table for analysis results |
| `ResumeParser-Backend-dev` | VPC, ECS Fargate, ALB |
| `ResumeParser-Frontend-dev` | CloudFront distribution + S3 static site |

### StorageStack
- S3 bucket with server-side encryption
- Lifecycle rules to expire uploads after 30 days
- Removal policy: DESTROY (dev environment)

### DatabaseStack
- DynamoDB table (`resume-analyzer-results`)
- PAY_PER_REQUEST billing (no capacity planning)
- Partition key: `id` (string)

### BackendStack
- VPC with 2 AZs and 1 NAT Gateway
- ECS Fargate service (256 CPU, 512MB memory)
- Application Load Balancer (public)
- Task IAM role with least-privilege permissions (S3, DynamoDB, Textract, Bedrock, SSM)
- Anthropic API key injected from SSM Parameter Store
- ALB idle timeout: 120s (for Claude AI response time)
- Docker image built for `linux/amd64` (works on Apple Silicon Macs)

### FrontendStack
- S3 bucket (private, block all public access)
- CloudFront distribution with OAC (Origin Access Control)
- `/api/v1/*` behaviour proxies to ALB (fixes mixed content, single HTTPS endpoint)
- CloudFront read timeout: 60s
- SPA routing: 404/403 → `index.html`
- Automatic cache invalidation on deploy

---

## Project Structure

```
infrastructure/
├── app.py                    # CDK entry point — wires all stacks
├── cdk.json                  # CDK config (profile: resume-parser)
├── requirements.txt          # CDK Python dependencies
├── stacks/
│   ├── storage_stack.py      # S3 bucket
│   ├── database_stack.py     # DynamoDB table
│   ├── backend_stack.py      # ECS Fargate + ALB + VPC
│   └── frontend_stack.py     # CloudFront + S3 static site
├── iam-deploy-policy-1.json  # IAM policy for CDK deploy user (part 1)
└── iam-deploy-policy-2.json  # IAM policy for CDK deploy user (part 2)
```

---

## Prerequisites

```bash
npm install -g aws-cdk
pip install -r infrastructure/requirements.txt
```

---

## One-Time Setup

### 1 — Configure AWS CLI profile

```bash
aws configure --profile resume-parser
```

### 2 — Store Anthropic API key in SSM

```bash
aws ssm put-parameter \
  --name "/resume-parser/dev/anthropic-api-key" \
  --value "sk-ant-your-key-here" \
  --type SecureString \
  --profile resume-parser
```

> Important: do not add a trailing newline to the key value.

### 3 — Bootstrap CDK (first time only)

```bash
cd infrastructure
cdk bootstrap --profile resume-parser
```

---

## Deploy

**Via Makefile (recommended — runs tests first):**
```bash
make deploy
```

**Manually:**
```bash
cd frontend && npm run build
cd infrastructure && cdk deploy --all
```

CDK reads `profile: resume-parser` from `cdk.json` automatically.

---

## Destroy

```bash
cd infrastructure
cdk destroy --all
```

> This deletes all AWS resources including S3 buckets and DynamoDB data.

---

## IAM Deploy Permissions

The `resume-parser` IAM user needs the policies in:
- `iam-deploy-policy-1.json` — ECS, EC2, ELB, IAM, CloudFront, CloudWatch
- `iam-deploy-policy-2.json` — S3, DynamoDB, SSM, ECR, Lambda, CloudFormation

Attach both policies to the deploy IAM user in AWS Console → IAM → Users → Add permissions → Create inline policy.


## Author

**Sanjay Patoliya**

- Email: sbpatoliya@gmail.com
- LinkedIn: https://linkedin.com/in/sanjaykumar-patoliya-b234a287/
- GitHub: https://github.com/sanjaypatoliya
- Portfolio: https://sanjaypatoliya.com
