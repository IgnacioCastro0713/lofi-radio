resource "google_storage_bucket" "lofi_audio_bucket" {
  name          = "${var.project_id}-lofi-audio-${var.environment}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  # Disable soft delete policy to prevent GCS from retaining deleted MP3 files for 7 days
  soft_delete_policy {
    retention_duration_seconds = 0
  }

  # Enable CORS so modern browsers can stream audio directly from Google Cloud Storage via Signed URLs
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # Rule autocleans objects older than 25 days to prevent storage bloat and match the 15-day sliding window
  lifecycle_rule {
    condition {
      age = 25 # Greater than 25 days
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
