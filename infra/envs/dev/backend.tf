terraform {
  backend "gcs" {
    bucket = "andela-meridian-prod-tfstate"
    prefix = "envs/dev"
  }
}
