variable "project_id" {
  type        = string
  description = "The GCP project ID."
}

variable "region" {
  type        = string
  description = "The GCP region to deploy the scheduler."
}

variable "environment" {
  type        = string
  description = "The deployment environment (e.g., dev, prod, staging)."
}

variable "job_name" {
  type        = string
  description = "The name of the Cloud Run Job to trigger."
}

variable "scheduler_sa_email" {
  type        = string
  description = "The service account email used by Cloud Scheduler."
}
