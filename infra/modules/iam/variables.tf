variable "project_id" {
  type        = string
  description = "The GCP project ID."
}

variable "environment" {
  type        = string
  description = "The deployment environment (e.g., dev, prod, staging)."
}
