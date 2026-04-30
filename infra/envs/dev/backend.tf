terraform {
  backend "gcs" {
    bucket = "meridian-tfstate-dev"
    prefix = "envs/dev"
  }
}
