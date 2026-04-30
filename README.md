# Meridian AI Customer Support Chatbot

LLM-powered customer-support chatbot for Meridian Electronics. The frontend signs the customer in with Clerk and chats with a FastAPI backend that proxies to Meridian's MCP server. The model, accessed through OpenRouter, discovers the MCP tools at startup and calls them inside a bounded tool-use loop to handle product browsing, customer verification, order history, and order placement.

## Stack

- **Backend**: FastAPI (Django-style apps), OpenAI SDK against OpenRouter, official MCP Python SDK over streamable HTTP, Clerk JWT verification via JWKS, slowapi rate limiting, structlog JSON logs.
- **Frontend**: React 18 + Vite + TypeScript + TanStack Query + Tailwind, Clerk for auth. Functional components only.
- **Infra**: Terraform on GCP — Cloud Run, Artifact Registry, Secret Manager, GCS-backed state.
- **CI**: GitHub Actions — backend lint/test, frontend typecheck/build/test, CodeQL, dependency review. Actions pinned to commit SHAs.

## Layout

```
meridian-ai-customer-support-chatbot/
├── backend/                   FastAPI service (Cloud Run)
│   ├── apps/
│   │   ├── chat/              ChatService — OpenRouter tool-use loop, system prompt, views
│   │   └── mcp/               McpClientService singleton, views
│   ├── core/                  settings, deps (Clerk JWT verifier), exceptions, logging
│   ├── tests/
│   ├── main.py                FastAPI app factory + lifespan
│   ├── manage.py              Typer CLI: runserver, probe-mcp
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                  React + Vite + TS + Clerk
│   └── src/
│       ├── features/chat/     ChatPage, MessageBubble, Composer, useChat
│       ├── lib/               env (Zod), api (axios + Clerk token)
│       ├── App.tsx            SignedIn / SignedOut gate
│       └── main.tsx           ClerkProvider, QueryClient
├── infra/
│   ├── envs/dev/              Terraform root for the dev environment
│   └── modules/               cloud_run_service, artifact_registry, secrets
└── .github/workflows/         backend-ci, frontend-ci, security, dependabot
```

## Prerequisites

- Python 3.12, Node 20+, Terraform 1.9+, Docker (for image builds), `gcloud` (for GCP).
- Clerk account with a publishable key and a Frontend API URL (issuer + JWKS).
- OpenRouter API key.

## Local development

### 1. MCP server reachability

The MCP server is shared. Confirm tools are reachable from your machine:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values
python manage.py probe-mcp
```

Expected output is the list of eight tools (`list_products`, `get_product`, `search_products`, `get_customer`, `verify_customer_pin`, `list_orders`, `get_order`, `create_order`).

### 2. Run the backend

```bash
python manage.py runserver
# → http://localhost:8000  (docs at /docs, health at /healthz)
```

### 3. Run the frontend

```bash
cd frontend
cp .env.example .env   # set VITE_CLERK_PUBLISHABLE_KEY
npm install
npm run dev
# → http://localhost:5173
```

Sign in with Clerk, then chat. The bot will ask you to verify with email + 4-digit PIN before showing order history or placing orders.

## Environment variables

### Backend (`backend/.env`)

| Var | Notes |
|---|---|
| `OPENROUTER_API_KEY` | Required. Stored in Secret Manager in prod. |
| `OPENROUTER_MODEL` | Model slug, e.g. `anthropic/claude-3.5-haiku`. |
| `OPENROUTER_BASE_URL` | Default `https://openrouter.ai/api/v1`. |
| `OPENROUTER_SITE_URL` | Optional. Sent as `HTTP-Referer` to OpenRouter. |
| `OPENROUTER_SITE_NAME` | Optional. Sent as `X-Title` to OpenRouter. |
| `MAX_TOOL_ITERATIONS` | Cap on agent loop iterations per turn. Default 8. |
| `MCP_SERVER_URL` | Streamable-HTTP endpoint of the MCP server. |
| `MCP_TIMEOUT_SECONDS` | Per-tool-call timeout. |
| `CLERK_ISSUER` | Clerk Frontend API URL, e.g. `https://your-app.clerk.accounts.dev`. |
| `CLERK_JWKS_URL` | Usually `<issuer>/.well-known/jwks.json`. |
| `CLERK_AUDIENCE` | Optional. Set if you configure `aud` claims in Clerk. |
| `CORS_ORIGINS` | Comma-separated list. |
| `RATE_LIMIT_CHAT` | slowapi rule, e.g. `20/minute`. |

### Frontend (`frontend/.env`)

| Var | Notes |
|---|---|
| `VITE_API_URL` | Backend base URL including `/api/v1`. |
| `VITE_APP_NAME` | Header label. |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key. |

## Deploying to GCP (sketch)

1. Create the GCS bucket `meridian-tfstate-dev` with uniform bucket-level access, versioning, and public-access prevention enforced.
2. Build and push the backend image to Artifact Registry: `gcloud builds submit backend --tag <repo>/backend:<sha>`.
3. `cd infra/envs/dev`, copy `terraform.tfvars.example` to `terraform.tfvars`, fill in the real values.
4. `terraform init && terraform plan && terraform apply`.
5. The output `backend_url` is the deployed Cloud Run URL.

CI auth to GCP should be Workload Identity Federation — no JSON keys in GitHub. The dev module skeleton is in place; wire `modules/github_oidc/` and a `deploy.yml` workflow when promoting to staging/prod.

## Security posture

- Clerk JWT verification on every protected route via JWKS, kid lookup, RS256.
- MCP tool results are treated as untrusted data. The system prompt forbids treating them as instructions.
- `create_order` is destructive. The system prompt requires the user to type `CONFIRM` before the tool fires; the chat UI surfaces every tool call and its arguments so the human in the loop can audit each action.
- Per-tool-call timeout, capped agent-loop iterations, and slowapi rate limiting on `/api/v1/chat`.
- No PII or auth payloads logged. Structured JSON logs for audit.
- Dependencies pinned; GitHub Actions pinned to commit SHAs; CodeQL + dependency review in CI.

## What was deliberately cut

- React UI deploy to Cloud Run static — left to Vercel during the sprint demo.
- Production Terraform environment and `deploy.yml` — dev module is wired, prod path is documented above.
- Persistent session storage — the chat is stateless per request. Conversations are reconstructed from the message history the client sends.
- Streaming responses — current `/chat` is request/response. Add SSE later by replacing the chat completions call with a streaming variant.

## Tests

```bash
cd backend && pytest -q
cd frontend && npm test
```

The backend tests cover the health endpoint and that `/chat` rejects unauthenticated requests. Add a richer suite (mocked MCP, mocked OpenRouter responses) before promoting.
