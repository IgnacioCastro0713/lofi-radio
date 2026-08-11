output "web_url" {
  value       = google_cloud_run_v2_service.lofi_web.uri
  description = "The public URL of the lofi web radio station."
}

output "job_name" {
  value       = google_cloud_run_v2_job.lofi_worker.name
  description = "The name of the music generator Cloud Run Job."
}
