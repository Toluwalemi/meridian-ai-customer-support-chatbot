# Deploy to GCP

Backend → Cloud Run via Terraform. Frontend → Vercel (fast). Total time on a prepared GCP account: 25–40 minutes.

The MCP server is already public (`https://order-mcp-74afyau24q-uc.a.run.app/mcp`) — you do not deploy that.

Set these once at the top of your shell so every command works:

```bash
export PROJECT_ID="meridian-prod-$(date +%s | tail -c 5)"   # globally unique
export REGION="us-central1"
export TFSTATE_BUCKET="${PROJECT_ID}-tfstate"
export REPO="meridian"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:v1"
```

---

## 0. Prerequisites

- `gcloud` CLI installed and authenticated: `gcloud auth login`.
- `terraform` 1.9+ on your PATH.
- Docker running.
- An OpenRouter API key (`sk-or-v1-...`).
- A Clerk app with a **production** publishable key and the Frontend API URL.

```bash
gcloud --version
terraform -version
docker info >/dev/null && echo "docker ok"
```

---

## 1. Create the GCP project and link billing

```bash
gcloud projects create "$PROJECT_ID" --name="Meridian Support"
gcloud config set project "$PROJECT_ID"

# Find your billing account id, then attach it.
gcloud beta billing accounts list
gcloud beta billing projects link "$PROJECT_ID" \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

**Verify**: `gcloud config get-value project` returns `$PROJECT_ID`.

---

## 2. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com
```

---

## 3. Create the Terraform state bucket

The bucket must exist **before** `terraform init` because it's the backend. Update `infra/envs/dev/backend.tf` if your bucket name differs from `meridian-tfstate-dev`.

```bash
gcloud storage buckets create "gs://${TFSTATE_BUCKET}" \
  --location="$REGION" \
  --uniform-bucket-level-access \
  --public-access-prevention

gcloud storage buckets update "gs://${TFSTATE_BUCKET}" --versioning
```

Edit `infra/envs/dev/backend.tf` and set `bucket = "<your TFSTATE_BUCKET>"`.

---

## 4. Configure Terraform variables

```bash
cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with real values:

| Variable | Value |
|---|---|
| `project_id` | `$PROJECT_ID` |
| `region` | `us-central1` |
| `environment` | `dev` |
| `backend_image` | `$IMAGE` |
| `openrouter_api_key` | your OpenRouter key |
| `clerk_issuer` | `https://<slug>.clerk.accounts.dev` |
| `clerk_jwks_url` | `https://<slug>.clerk.accounts.dev/.well-known/jwks.json` |
| `cors_origins` | `["https://<placeholder-frontend>.vercel.app"]` (you'll update after step 9) |

**Do not** commit `terraform.tfvars`.

---

## 5. Bootstrap the Artifact Registry (so we can push the image)

The Cloud Run service depends on an image that doesn't exist yet, so apply only the registry module first.

```bash
terraform init
terraform apply -target=module.artifact_registry -auto-approve
```

**Verify**:

```bash
gcloud artifacts repositories list --location="$REGION"
```

---

## 6. Build and push the backend image

From the repo root (not `infra/envs/dev`):

```bash
cd ../../..
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Apple Silicon: force linux/amd64 so Cloud Run can run the image.
docker buildx build --platform linux/amd64 \
  -t "$IMAGE" backend --load
docker push "$IMAGE"
```

**Verify**:

```bash
gcloud artifacts docker images list \
  "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}"
```

---

## 7. Apply the full Terraform plan

```bash
cd infra/envs/dev
terraform plan -out=tfplan
terraform apply tfplan
```

Capture the output:

```bash
terraform output -raw backend_url
# https://meridian-backend-dev-xxxxxx-uc.a.run.app
```

Save this URL — you need it in steps 8 and 9.

---

## 8. Smoke-test the backend

```bash
BACKEND_URL=$(terraform output -raw backend_url)

curl -s "${BACKEND_URL}/healthz" | jq
# {"status":"ok","env":"dev"}

curl -i -s -X POST "${BACKEND_URL}/api/v1/chat" \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
# HTTP/2 401 — good, Clerk JWT required.
```

A `401` here is success: it means routing, CORS, and the rate limiter all work, and the auth gate is enforced.

If `/healthz` returns 5xx, check Cloud Run logs:

```bash
gcloud run services logs read meridian-backend-dev \
  --region="$REGION" --limit=100
```

Most common cause: the image was built for `arm64`. Re-run step 6 with `--platform linux/amd64`.

---

## 9. Deploy the frontend on Vercel

From the repo root:

```bash
cd frontend
npm install
npx vercel --yes
```

When Vercel asks, add these environment variables (Production scope):

| Var | Value |
|---|---|
| `VITE_API_URL` | `<BACKEND_URL>/api/v1` |
| `VITE_APP_NAME` | `Meridian Support` |
| `VITE_CLERK_PUBLISHABLE_KEY` | your Clerk publishable key |

Then deploy:

```bash
npx vercel --prod
```

Note the resulting URL, e.g. `https://meridian-support.vercel.app`.

---

## 10. Wire CORS and Clerk to the real frontend URL

### 10a. Update Terraform CORS

In `infra/envs/dev/terraform.tfvars`, replace the placeholder Vercel URL in `cors_origins` with the real one:

```hcl
cors_origins = ["https://meridian-support.vercel.app"]
```

Then re-apply:

```bash
cd infra/envs/dev
terraform apply -auto-approve
```

This rolls a new Cloud Run revision with the real `CORS_ORIGINS`.

### 10b. Allow the Vercel domain in Clerk

In the Clerk dashboard → your app → **Domains**, add the Vercel URL as an allowed origin. In **Sessions / JWT Templates**, confirm the issuer matches what's in `CLERK_ISSUER`.

---

## 11. End-to-end test in the browser

1. Open the Vercel URL.
2. Sign in with Clerk.
3. Try the prompts from `backend/tests/fixtures/demo_prompts.md`. The catalog browse and the order-history flows should both succeed.
4. Confirm in Cloud Run logs that requests are coming through with structured JSON entries.

---

## What you skipped (and what to do for prod)

- **Workload Identity Federation for CI**: this guide deploys from your laptop. For prod, add `infra/modules/github_oidc/` and a `deploy.yml` workflow that uses `google-github-actions/auth` with WIF. No JSON keys in GitHub.
- **`prod` environment**: clone `infra/envs/dev/` → `infra/envs/prod/` with its own state prefix and a separate runtime SA. Promote via PR.
- **Custom domain + HTTPS**: map a Cloud Run domain in Cloud Run console, or front it with Cloud Load Balancer + Google-managed cert.
- **Min instances**: bump `min_instances` in the Cloud Run module from 0 to 1 to remove cold starts.
- **Frontend on Cloud Run**: only worth the swap if you need to keep all traffic in GCP. Otherwise Vercel is fine.

---

## Common gotchas

| Symptom | Fix |
|---|---|
| `failed precondition: project … billing not enabled` | Step 1, link billing. |
| `terraform init` fails with bucket 404 | Create the bucket (step 3) **before** init. |
| Cloud Run revision crashes immediately | `gcloud run services logs read …`. Usually a missing env var or wrong-architecture image. |
| Cloud Run revision starts but `/chat` is 502 | Backend can't reach the MCP server or the LLM. Check `OPENROUTER_API_KEY` is mounted (Secret Manager IAM) and `MCP_SERVER_URL` is correct. |
| Browser shows a CORS error | `cors_origins` doesn't include the exact Vercel origin. Step 10a. |
| `401` from `/chat` in the browser even after sign-in | Clerk JWKS URL is wrong or the Vercel domain isn't allowlisted in Clerk. Step 10b. |
| Local laptop deploy works, GitHub Actions doesn't | You're missing WIF. Don't paste a service-account JSON key — set up Workload Identity Federation. |

---

## Tear down (avoid surprise charges)

```bash
cd infra/envs/dev
terraform destroy -auto-approve

gcloud storage rm -r "gs://${TFSTATE_BUCKET}"
gcloud projects delete "$PROJECT_ID"
```
