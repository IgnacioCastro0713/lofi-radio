variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy resources into (DEV)."
}

variable "region" {
  type        = string
  description = "The GCP region to deploy resources into (DEV)."
  default     = "us-central1"
}

variable "image_tag" {
  type        = string
  description = "The docker image tag to deploy (DEV)."
  default     = "latest"
}

variable "track_count" {
  type        = number
  description = "The number of daily looping tracks to generate (e.g., 100)"
  default     = 100
}
