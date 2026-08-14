# 1. Cloud Run Service for the Blazor Web App / API
resource "google_cloud_run_v2_service" "lofi_web" {
  name     = "lofi-web-service-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

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

# Make the Cloud Run Web App publicly accessible (Requires roles/run.invoker for public HTTP traffic)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.lofi_web.name
  location = google_cloud_run_v2_service.lofi_web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 2. Cloud Run Job for the Music Generator Worker
resource "google_cloud_run_v2_job" "lofi_worker" {
  name     = "lofi-generator-job-${var.environment}"
  location = var.region

  template {
    task_count  = 1
    template {
      max_retries     = 0 # Disable automatic retries to save CPU, billing, and Vertex API quota if a sequential run fails!
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
