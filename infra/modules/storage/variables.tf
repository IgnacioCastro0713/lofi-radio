variable "project_id" {
  type        = string
  description = "The GCP project ID."
}

variable "region" {
  type        = string
  description = "The region to deploy the storage bucket."
}

variable "environment" {
  type        = string
  description = "The deployment environment (e.g., dev, prod, staging)."
}

variable "worker_sa_email" {
  type        = string
  description = "The email of the worker service account."
}

variable "web_sa_email" {
  type        = string
  description = "The email of the web service account."
}
