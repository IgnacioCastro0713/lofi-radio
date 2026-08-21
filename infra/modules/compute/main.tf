# Project number needed for the IAP service agent's invoker binding.
data "google_project" "current" {
  project_id = var.project_id
}

# Required for the IAP IAM binding below; enable once so `apply` doesn't fail on a fresh project.
resource "google_project_service" "iap" {
  project            = var.project_id
  service            = "iap.googleapis.com"
  disable_on_destroy = false
}

# 1. Cloud Run Service for the Blazor Web App / API
resource "google_cloud_run_v2_service" "lofi_web" {
  provider    = google-beta
  name        = "lofi-web-service-${var.environment}"
  location    = var.region
  ingress     = "INGRESS_TRAFFIC_ALL"
  iap_enabled = length(var.iap_authorized_domains) > 0 ? true : false

  template {
    service_account  = var.web_sa_email
    session_affinity = true # Enforces Session Affinity (sticky sessions) for Blazor Server SignalR/WebSockets!

    # 🛡️ Wallet-Busting & Billing DDoS Shield: Limit max instances to 2.
    # NET 10 can easily serve thousands of concurrent listeners with just 2 instances,
    # completely capping your maximum cloud bill to pocket change under any brutal DDoS attack!
    scaling {
      max_instance_count = 2
    }

    containers {
      image = "gcr.io/${var.project_id}/lofi-web-${var.environment}:${var.image_tag}"

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_BUCKET_NAME"
        value = var.bucket_name
      }

      env {
        name  = "TRACK_COUNT"
        value = tostring(var.track_count)
      }

      env {
        name  = "ASPNETCORE_ENVIRONMENT"
        value = "Production"
      }

      ports {
        container_port = 8080
      }
    }
  }
}

# IAP now gates access instead of allUsers: only members below reach lofi_web.
resource "google_iap_web_cloud_run_service_iam_binding" "iap_access" {
  count                  = length(var.iap_authorized_domains) > 0 ? 1 : 0
  provider               = google-beta
  project                = var.project_id
  location               = google_cloud_run_v2_service.lofi_web.location
  cloud_run_service_name = google_cloud_run_v2_service.lofi_web.name
  role                   = "roles/iap.httpsResourceAccessor"
  members                = var.iap_authorized_domains

  depends_on = [google_project_service.iap]
}

# IAP's service agent needs run.invoker to forward authenticated requests to the service.
resource "google_cloud_run_v2_service_iam_member" "iap_invoker" {
  count    = length(var.iap_authorized_domains) > 0 ? 1 : 0
  project  = var.project_id
  location = google_cloud_run_v2_service.lofi_web.location
  name     = google_cloud_run_v2_service.lofi_web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-iap.iam.gserviceaccount.com"
}

# Public access allowed when IAP is disabled.
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count    = length(var.iap_authorized_domains) == 0 ? 1 : 0
  project  = var.project_id
  location = google_cloud_run_v2_service.lofi_web.location
  name     = google_cloud_run_v2_service.lofi_web.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 2. Cloud Run Job for the Music Generator Worker
resource "google_cloud_run_v2_job" "lofi_worker" {
  name     = "lofi-generator-job-${var.environment}"
  location = var.region

  template {
    task_count = 1
    template {
      max_retries     = 0       # Disable automatic retries to save CPU, billing, and Vertex API quota if a sequential run fails!
      timeout         = "7200s" # 2 hours (120 minutes) max life to ensure 100 tracks generate successfully under any GCR/Vertex latency!
      service_account = var.worker_sa_email

      containers {
        image = "gcr.io/${var.project_id}/lofi-worker-${var.environment}:${var.image_tag}"

        env {
          name  = "GCS_BUCKET_NAME"
          value = var.bucket_name
        }

        env {
          name  = "TRACK_COUNT"
          value = tostring(var.track_count)
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "GCP_REGION"
          value = var.region
        }

        env {
          name  = "USE_REAL_LYRIA"
          value = "true"
        }

        env {
          name  = "MUSIC_MODEL"
          value = var.music_model
        }

        env {
          name  = "IMAGE_MODEL"
          value = var.image_model
        }
      }
    }
  }
}
