# Frontend — React

React 18 + TypeScript + Vite + TailwindCSS single-page application. Communicates with the FastAPI backend via Axios and TanStack Query.

---

## Pages

| Page | Route | Description |
|---|---|---|
| Home | `/` | Upload resume PDF + paste job description |
| Results | `/results?id=<id>` | Score gauge, category breakdown, skills, suggestions |
| History | `/history` | Recent analyses with View and Delete per record |

---

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts              # Axios instance (VITE_API_URL base)
│   ├── components/
│   │   └── UploadZone.tsx         # Drag-and-drop PDF upload
│   ├── hooks/
│   │   ├── useUpload.ts           # S3 direct upload with progress
│   │   ├── useAnalysis.ts         # Analysis submission + loading states
│   │   ├── useHistory.ts          # TanStack Query history fetch
│   │   └── useDeleteHistory.ts    # Delete one or many history items
│   ├── pages/
│   │   ├── HomePage.tsx           # Upload form
│   │   ├── ResultsPage.tsx        # Analysis results display
│   │   └── HistoryPage.tsx        # History list with View/Delete
│   ├── types/
│   │   └── index.ts               # TypeScript interfaces
│   └── tests/
│       ├── setup.ts               # jest-dom matchers
│       ├── hooks/                 # Hook unit tests
│       ├── components/            # Component tests
│       └── pages/                 # Page integration tests
├── .env.example
├── .env.production                # VITE_API_URL=/api/v1 (CloudFront routing)
├── index.html
├── vite.config.ts
└── package.json
```

---

## Local Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App runs at **http://localhost:5173**

> Make sure the backend is running at `http://localhost:8000` before testing locally.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend API base URL | `/api/v1` |

- **Local dev:** set `VITE_API_URL=http://localhost:8000/api/v1` in `.env`
- **Production:** uses `/api/v1` (relative path — CloudFront routes to ALB)

---

## Running Tests

```bash
cd frontend

# Run all tests
npm test

# Watch mode (re-runs on file save)
npm run test:watch

# With coverage report
npm run test:coverage
```

**Test coverage:**
- Minimum threshold: **70%**
- HTML report: open `coverage/index.html` in browser

**Test structure:**
```
src/tests/
├── setup.ts
├── hooks/
│   ├── useUpload.test.ts       (5 tests)
│   ├── useAnalysis.test.ts     (4 tests)
│   └── useHistory.test.ts      (3 tests)
├── components/
│   └── UploadZone.test.tsx     (4 tests)
└── pages/
    ├── HomePage.test.tsx       (6 tests)
    ├── ResultsPage.test.tsx    (9 tests)
    └── HistoryPage.test.tsx    (7 tests — updated for View/Delete UI)
```

---

## Production Build

```bash
npm run build
```

Output goes to `dist/` — this is what CDK deploys to S3.


## Author

**Sanjay Patoliya**

- Email: sbpatoliya@gmail.com
- LinkedIn: https://linkedin.com/in/sanjaykumar-patoliya-b234a287/
- GitHub: https://github.com/sanjaypatoliya
- Portfolio: https://sanjaypatoliya.com
