output "bucket_name" {
  value       = google_storage_bucket.lofi_audio_bucket.name
  description = "The name of the lofi audio GCS bucket."
}
