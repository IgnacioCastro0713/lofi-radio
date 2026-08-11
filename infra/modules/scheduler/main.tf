# Grant Cloud Run Invoker to Scheduler SA specifically on the worker job
resource "google_cloud_run_v2_job_iam_member" "scheduler_invoker" {
  name     = var.job_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.scheduler_sa_email}"
}

# Cloud Scheduler trigger configured to execute daily strictly from Monday to Friday at 6:00 AM UTC
resource "google_cloud_scheduler_job" "trigger_lofi_generator" {
  name        = "trigger-lofi-generator-job-${var.environment}"
  description = "Triggers the lofi tracks buffer generation daily from Mon-Fri at 6:00 AM UTC (${var.environment})"
  schedule    = "0 6 * * 1-5"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    
    oauth_token {
      service_account_email = var.scheduler_sa_email
    }
  }

  depends_on = [google_cloud_run_v2_job_iam_member.scheduler_invoker]
}
