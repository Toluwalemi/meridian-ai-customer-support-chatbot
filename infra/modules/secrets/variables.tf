variable "project_id" {
  type = string
}

variable "secrets" {
  type        = map(string)
  description = "Map of secret name to plaintext value. Values are sensitive."
  sensitive   = true
}
