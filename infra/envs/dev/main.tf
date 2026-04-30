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
    anthropic-api-key = var.anthropic_api_key
  }
}

module "backend" {
  source       = "../../modules/cloud_run_service"
  project_id   = var.project_id
  region       = var.region
  service_name = "meridian-backend-${var.environment}"
  image        = var.backend_image

  env = {
    APP_NAME       = "meridian-support-chatbot"
    ENV            = var.environment
    DEBUG          = "false"
    MCP_SERVER_URL = var.mcp_server_url
    CLERK_ISSUER   = var.clerk_issuer
    CLERK_JWKS_URL = var.clerk_jwks_url
    CORS_ORIGINS   = join(",", var.cors_origins)
  }

  secret_env = {
    ANTHROPIC_API_KEY = module.secrets.secret_ids["anthropic-api-key"]
  }
}
