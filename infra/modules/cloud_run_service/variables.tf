variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "service_name" {
  type = string
}

variable "image" {
  type = string
}

variable "env" {
  type    = map(string)
  default = {}
}

variable "secret_env" {
  type        = map(string)
  description = "Map of env var name to Secret Manager secret_id."
  default     = {}
}

variable "min_instances" {
  type    = number
  default = 0
}

variable "max_instances" {
  type    = number
  default = 5
}

variable "allow_unauthenticated" {
  type    = bool
  default = true
}
