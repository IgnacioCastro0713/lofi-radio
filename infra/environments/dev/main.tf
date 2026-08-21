terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.0"
    }
  }
  backend "gcs" {
    bucket = "lofi-radio-tfstate"
    prefix = "dev/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

locals {
  environment = "dev"
}

# 1. Firestore Database - Provisions native Google Cloud Firestore database
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# 2. IAM Module - Creates dedicated Service Accounts and grants Roles for DEV
module "iam" {
  source      = "../../modules/iam"
  project_id  = var.project_id
  environment = local.environment
}

# 3. Storage Module - Sets up the GCS bucket and binds access permissions for DEV
module "storage" {
  source          = "../../modules/storage"
  project_id      = var.project_id
  region          = var.region
  environment     = local.environment
  worker_sa_email = module.iam.worker_sa_email
  web_sa_email    = module.iam.web_sa_email
}

# 4. Compute Module - Deploys Cloud Run Service & Job using serverless native Firestore
module "compute" {
  source                 = "../../modules/compute"
  project_id             = var.project_id
  region                 = var.region
  environment            = local.environment
  image_tag              = var.image_tag
  worker_sa_email        = module.iam.worker_sa_email
  web_sa_email           = module.iam.web_sa_email
  bucket_name            = module.storage.bucket_name
  track_count            = var.track_count
  music_model            = var.music_model
  image_model            = var.image_model
  iap_authorized_domains = var.iap_authorized_domains

  depends_on = [google_firestore_database.database, module.storage]
}

# 5. Scheduler Module - Schedules periodic execution of the Worker Job for DEV
module "scheduler" {
  source             = "../../modules/scheduler"
  project_id         = var.project_id
  region             = var.region
  environment        = local.environment
  job_name           = module.compute.job_name
  scheduler_sa_email = module.iam.scheduler_sa_email

  depends_on = [module.compute]
}

# Root Outputs
output "lofi_radio_web_url" {
  value       = module.compute.web_url
  description = "The public web URL of your lofi radio station stream (DEV)!"
}
