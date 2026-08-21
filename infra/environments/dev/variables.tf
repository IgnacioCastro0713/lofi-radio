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

variable "music_model" {
  type        = string
  description = "The DeepMind music generation model name (DEV)."
  default     = "lyria-3-pro-preview"
}

variable "image_model" {
  type        = string
  description = "The Gemini image generation model name (DEV)."
  default     = "gemini-3.1-flash-image"
}

variable "iap_authorized_domains" {
  type        = list(string)
  description = "IAM members granted roles/iap.httpsResourceAccessor for the IAP-gated site (DEV)."
  default     = []
}
