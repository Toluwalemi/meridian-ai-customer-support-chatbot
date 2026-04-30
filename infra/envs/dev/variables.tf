variable "project_id" {
  type        = string
  description = "GCP project id."
  validation {
    condition     = length(var.project_id) > 0
    error_message = "project_id must not be empty."
  }
}

variable "region" {
  type        = string
  description = "GCP region."
  default     = "us-central1"
  validation {
    condition     = contains(["us-central1", "us-east1", "us-west1", "europe-west1"], var.region)
    error_message = "Use a supported region."
  }
}

variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "owner" {
  type    = string
  default = "platform"
}

variable "backend_image" {
  type        = string
  description = "Fully-qualified Artifact Registry image for the backend, e.g. us-central1-docker.pkg.dev/PROJECT/meridian/backend:GIT_SHA"
}

variable "anthropic_api_key" {
  type      = string
  sensitive = true
}

variable "mcp_server_url" {
  type    = string
  default = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
}

variable "clerk_issuer" {
  type = string
}

variable "clerk_jwks_url" {
  type = string
}

variable "cors_origins" {
  type    = list(string)
  default = ["http://localhost:5173"]
}
