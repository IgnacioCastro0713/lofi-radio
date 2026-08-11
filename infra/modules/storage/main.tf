resource "google_storage_bucket" "lofi_audio_bucket" {
  name          = "${var.project_id}-lofi-audio-${var.environment}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  # Rule autocleans objects older than 1 day (24 hours) to prevent storage bloat and reduce costs
  lifecycle_rule {
    condition {
      age = 1 # Greater than 24 hours (1 day)
    }
    action {
      type = "Delete"
    }
  }
}

# Grant objectUser to Worker (allows listing, creating, and deleting MP3s for daily cleanup under least privilege)
resource "google_storage_bucket_iam_member" "worker_creator" {
  bucket = google_storage_bucket.lofi_audio_bucket.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${var.worker_sa_email}"
}

# Grant objectViewer to Web (GCS bucket is private, we will stream via the Web App proxy!)
resource "google_storage_bucket_iam_member" "web_viewer" {
  bucket = google_storage_bucket.lofi_audio_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.web_sa_email}"
}
