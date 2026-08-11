resource "google_service_account" "worker_sa" {
  account_id   = "lofi-worker-sa-${var.environment}"
  display_name = "Lofi Radio Music Generator Worker Service Account (${var.environment})"
}

resource "google_service_account" "web_sa" {
  account_id   = "lofi-web-sa-${var.environment}"
  display_name = "Lofi Radio Blazor Web Service Account (${var.environment})"
}

resource "google_service_account" "scheduler_sa" {
  account_id   = "lofi-scheduler-sa-${var.environment}"
  display_name = "Lofi Radio Scheduler Service Account (${var.environment})"
}

# Grant Vertex AI User to Worker (to call Lyria 3 Pro preview API)
resource "google_project_iam_member" "worker_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.worker_sa.email}"
}

# Grant Datastore User (Firestore native access) to Worker & Web SAs
resource "google_project_iam_member" "worker_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.worker_sa.email}"
}

resource "google_project_iam_member" "web_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.web_sa.email}"
}

# Grant BigQuery Job User to Worker SA
resource "google_project_iam_member" "worker_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.worker_sa.email}"
}
