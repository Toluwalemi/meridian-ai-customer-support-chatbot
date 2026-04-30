# Meridian AI Customer Support Chatbot

> ## Live demo
> ### **[https://meridian-frontend-dev-zib44qu2wq-ew.a.run.app](https://meridian-frontend-dev-zib44qu2wq-ew.a.run.app)**
>
> Backend API: `https://meridian-backend-dev-zib44qu2wq-ew.a.run.app`
> Region: `europe-west1` · Both services on Cloud Run, scale-to-zero (~2 s cold start).

LLM-powered customer-support chatbot for Meridian Electronics. The frontend signs the customer in with Clerk and chats with a FastAPI backend that proxies to Meridian's MCP server. The model, accessed through OpenRouter, discovers the MCP tools at startup and calls them inside a bounded tool-use loop to handle product browsing, customer verification, order history, and order placement.

## Try it

1. Open the frontend URL above.
2. Sign in with Clerk (any email; verification by code).
3. Use a test customer from `backend/tests/fixtures/test_customers.md` — for example `donaldgarcia@example.net` / PIN `7912`.
4. Walk a scenario from `backend/tests/fixtures/demo_prompts.md` — anonymous browse, authenticated order history, or a `CONFIRM`-gated order placement.

## Stack

- **Backend**: FastAPI OpenAI SDK against OpenRouter, official MCP Python SDK over streamable HTTP, Clerk JWT verification via JWKS, slowapi rate limiting, structlog JSON logs.
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

- Python 3, Node 20+, Terraform 1.9+, Docker (for image builds), `gcloud` (for GCP).
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


### Frontend (`frontend/.env`)

| Var | Notes |
|---|---|
| `VITE_API_URL` | Backend base URL including `/api/v1`. |
| `VITE_APP_NAME` | Header label. |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key. |


## Tests

```bash
cd backend && pytest -q
cd frontend && npm test
``
docker buildx build --platform linux/amd64 -t europe-west1-docker.pkg.dev/andela-meridian-prod/meridian-ai-customer-support-chatbot backend:v1 backend --load
