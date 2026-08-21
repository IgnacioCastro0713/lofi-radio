variable "project_id" {
  type        = string
  description = "The GCP project ID."
}

variable "region" {
  type        = string
  description = "The region to deploy Cloud Run resources."
}

variable "environment" {
  type        = string
  description = "The deployment environment (e.g., dev, prod, staging)."
}

variable "image_tag" {
  type        = string
  description = "The docker image tag to deploy."
  default     = "latest"
}

variable "worker_sa_email" {
  type        = string
  description = "The email of the worker service account."
}

variable "web_sa_email" {
  type        = string
  description = "The email of the web service account."
}

variable "bucket_name" {
  type        = string
  description = "The name of the GCS bucket."
}

variable "track_count" {
  type        = number
  description = "The number of daily looping tracks to generate (e.g., 100)"
  default     = 100
}

variable "music_model" {
  type        = string
  description = "The DeepMind music generation model name."
  default     = "lyria-3-pro-preview"
}

variable "image_model" {
  type        = string
  description = "The Gemini image generation model name."
  default     = "gemini-3.1-flash-image"
}

variable "iap_authorized_domains" {
  type        = list(string)
  description = "IAM members granted roles/iap.httpsResourceAccessor (e.g. \"domain:example.com\", \"user:me@example.com\")."
  default     = []
}
