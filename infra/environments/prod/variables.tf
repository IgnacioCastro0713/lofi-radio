variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy resources into (PROD)."
}

variable "region" {
  type        = string
  description = "The GCP region to deploy resources into (PROD)."
  default     = "us-central1"
}

variable "image_tag" {
  type        = string
  description = "The docker image tag to deploy (PROD)."
  default     = "latest"
}
