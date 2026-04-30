locals {
  secret_names = nonsensitive(toset(keys(var.secrets)))
}

resource "google_secret_manager_secret" "this" {
  for_each = local.secret_names

  project   = var.project_id
  secret_id = each.key

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "this" {
  for_each = local.secret_names

  secret      = google_secret_manager_secret.this[each.key].id
  secret_data = var.secrets[each.key]
}
