resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repo_id
  format        = "DOCKER"
  description   = "Meridian container images"
}
