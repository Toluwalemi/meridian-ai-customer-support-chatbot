provider "google" {
  project = var.project_id
  region  = var.region

  default_labels = {
    project     = "meridian-support-chatbot"
    environment = var.environment
    managed_by  = "terraform"
    owner       = var.owner
  }
}

module "artifact_registry" {
  source     = "../../modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
  repo_id    = "meridian"
}

module "secrets" {
  source     = "../../modules/secrets"
  project_id = var.project_id
  secrets = {
    openrouter-api-key = var.openrouter_api_key
  }
}

module "backend" {
  source       = "../../modules/cloud_run_service"
  project_id   = var.project_id
  region       = var.region
  service_name = "meridian-backend-${var.environment}"
  image        = var.backend_image

  env = {
    APP_NAME          = "meridian-support-chatbot"
    ENV               = var.environment
    DEBUG             = "false"
    OPENROUTER_MODEL  = var.openrouter_model
    MCP_SERVER_URL    = var.mcp_server_url
    CLERK_ISSUER      = var.clerk_issuer
    CLERK_JWKS_URL    = var.clerk_jwks_url
    CORS_ORIGINS      = join(",", var.cors_origins)
    AUTH_DEV_BYPASS   = "false"
  }

  secret_env = {
    OPENROUTER_API_KEY = module.secrets.secret_ids["openrouter-api-key"]
  }
}

module "frontend" {
  source       = "../../modules/cloud_run_service"
  project_id   = var.project_id
  region       = var.region
  service_name = "meridian-frontend-${var.environment}"
  image        = var.frontend_image
}
