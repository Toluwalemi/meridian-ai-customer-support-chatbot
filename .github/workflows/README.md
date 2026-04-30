# GitHub Actions

## `terraform.yml` — manual plan / apply / destroy

Triggered manually from the Actions tab. Inputs:

| Input | Choices | Notes |
|---|---|---|
| `action` | `plan` / `apply` / `destroy` | What to run. |
| `environment` | `dev` | Picks `infra/envs/<env>/` as the working directory. |
| `destroy_confirmation` | string | Must be `DESTROY` when action is `destroy`. |

Behaviour:

- `plan` — runs `terraform plan`, posts the plan to the workflow summary, uploads the binary plan as an artifact (`tfplan-<env>-<run_id>`).
- `apply` — runs `plan` first (so the summary still shows the plan), then `terraform apply` against the freshly produced plan file. Outputs are posted to the summary.
- `destroy` — runs `terraform destroy -auto-approve`, but only if `destroy_confirmation=DESTROY`. The job aborts otherwise.

Auth uses **Workload Identity Federation** — no service-account JSON keys in GitHub secrets.

---

## One-time setup (per GCP project)

Run these locally with the same gcloud account that owns the project. Replace `andela-meridian-prod` if you're deploying to a different project. The repo placeholder is `OWNER/REPO`.

### 1. Variables

```bash
export PROJECT_ID="andela-meridian-prod"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
export REPO="OWNER/REPO"           # e.g. lemiteksolutions/meridian-ai-customer-support-chatbot
export DEPLOY_SA="meridian-deploy"
export POOL="github-pool"
export PROVIDER="github-provider"
```

### 2. Enable the IAM Credentials API

```bash
gcloud services enable iamcredentials.googleapis.com --project="$PROJECT_ID"
```

### 3. Create the deploy service account and grant it the roles Terraform needs

```bash
gcloud iam service-accounts create "$DEPLOY_SA" \
  --project="$PROJECT_ID" \
  --display-name="Meridian Terraform deployer"

DEPLOY_SA_EMAIL="${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

for role in \
  roles/run.admin \
  roles/artifactregistry.admin \
  roles/secretmanager.admin \
  roles/iam.serviceAccountAdmin \
  roles/iam.serviceAccountUser \
  roles/storage.admin \
  roles/serviceusage.serviceUsageAdmin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
    --role="$role" \
    --condition=None \
    --quiet
done
```

`storage.admin` is for the GCS state bucket. Tighten to `storage.objectAdmin` on just that bucket once everything works.

### 4. Create the workload identity pool and a GitHub OIDC provider

```bash
gcloud iam workload-identity-pools create "$POOL" \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub pool"

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="$POOL" \
  --display-name="GitHub Actions" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref,attribute.actor=assertion.actor" \
  --attribute-condition="assertion.repository=='${REPO}'"
```

### 5. Allow your repo to impersonate the deploy SA

```bash
gcloud iam service-accounts add-iam-policy-binding "$DEPLOY_SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/attribute.repository/${REPO}"
```

### 6. Print the values you need to put in GitHub

```bash
echo "GCP_PROJECT_ID      = $PROJECT_ID"
echo "GCP_WIF_PROVIDER    = projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/providers/${PROVIDER}"
echo "GCP_DEPLOY_SA       = $DEPLOY_SA_EMAIL"
```

---

## GitHub configuration

In your repo → **Settings → Secrets and variables → Actions**.

### Repository secrets

| Name | Value |
|---|---|
| `OPENROUTER_API_KEY` | your `sk-or-v1-...` |

### Repository variables

| Name | Value |
|---|---|
| `GCP_PROJECT_ID` | `andela-meridian-prod` |
| `GCP_REGION` | `europe-west1` |
| `GCP_WIF_PROVIDER` | `projects/<NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_DEPLOY_SA` | `meridian-deploy@andela-meridian-prod.iam.gserviceaccount.com` |
| `OWNER` | `platform` |
| `BACKEND_IMAGE` | `europe-west1-docker.pkg.dev/andela-meridian-prod/meridian/backend:v2` |
| `FRONTEND_IMAGE` | `europe-west1-docker.pkg.dev/andela-meridian-prod/meridian/frontend:v2` |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-haiku` |
| `MCP_SERVER_URL` | `https://order-mcp-74afyau24q-uc.a.run.app/mcp` |
| `CLERK_ISSUER` | `https://possible-colt-10.clerk.accounts.dev` |
| `CLERK_JWKS_URL` | `https://possible-colt-10.clerk.accounts.dev/.well-known/jwks.json` |
| `CLERK_PUBLISHABLE_KEY` | `pk_test_cG9zc2libGUtY29sdC0xMC5jbGVyay5hY2NvdW50cy5kZXYk` |
| `CORS_ORIGINS` | `["https://meridian-frontend-dev-zib44qu2wq-ew.a.run.app"]` |

`CORS_ORIGINS` is set as a JSON array because the Terraform variable is `list(string)` and `TF_VAR_*` env vars take JSON syntax for complex types.

### GitHub Environment

Create an environment named `dev` (Settings → Environments). For prod later, add a `prod` environment with required reviewers — that gives you a manual approval gate before `apply`/`destroy` runs.

---

## Running the workflow

Actions → **terraform** → **Run workflow** → pick `dev` and one of `plan` / `apply` / `destroy`.

For destroy you must also set `destroy_confirmation` to the literal string `DESTROY`.

---

## What this workflow does NOT do

- **Build images.** Image tags come in via `BACKEND_IMAGE` / `FRONTEND_IMAGE` repo variables. Add a separate `build-images.yml` workflow when you want CI-built images.
- **Promote across environments.** Each environment has its own working directory; no cross-env state coupling.
- **Rotate secrets.** Secret Manager values are managed by Terraform but pulled from GitHub secrets; rotate at the source.
