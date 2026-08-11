output "worker_sa_email" {
  value       = google_service_account.worker_sa.email
  description = "The email of the worker service account."
}

output "web_sa_email" {
  value       = google_service_account.web_sa.email
  description = "The email of the web service account."
}

output "scheduler_sa_email" {
  value       = google_service_account.scheduler_sa.email
  description = "The email of the scheduler service account."
}
