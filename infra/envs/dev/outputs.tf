output "backend_url" {
  value       = module.backend.service_url
  description = "Public URL of the backend Cloud Run service."
}

output "artifact_registry_repository" {
  value       = module.artifact_registry.repository_url
  description = "Docker repository URL for backend images."
}
