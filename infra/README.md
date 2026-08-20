# ☁️ GCP Infrastructure APIs & Services Manual 👾🌅🌇🌌

This directory manages the serverless Infrastructure as Code (IaC) for **LofiRadio** using Terraform. 

Before running `terraform apply`, you must ensure that your Google Cloud Project has the following official GCP APIs enabled. Without these APIs, Google Cloud will reject the resource provisioning.

---

## 🛠️ Required Google Cloud APIs Matrix

| GCP API Service Name | Terraform Identifier | Used For / Resource Association |
| :--- | :--- | :--- |
| **Cloud Run API** | `run.googleapis.com` | Hosting both the serverless Blazor Web container and the Python Worker job. |
| **Cloud Firestore API** | `firestore.googleapis.com` | Provisioning and managing the native serverless NoSQL database. |
| **Cloud Datastore API** | `datastore.googleapis.com` | Required internally by GCP for NoSQL database metadata management. |
| **Cloud Storage API** | `storage.googleapis.com` | Storing and managing the private `.mp3` AI-generated audio files. |
| **Vertex AI API** | `aiplatform.googleapis.com` | Accessing Google DeepMind Lyria 3 Pro to generate the lofi music. |
| **Cloud Scheduler API** | `scheduler.googleapis.com` | Automating the Mon-Fri daily trigger of the Python worker job. |
| **BigQuery API** | `bigquery.googleapis.com` | Required internally by Vertex AI for model usage metrics and ingestion. |
| **IAM API** | `iam.googleapis.com` | Provisioning dedicated secure Service Accounts (`sa-web` and `sa-worker`). |
| **IAM Credentials API** | `iamcredentials.googleapis.com` | Required for programmatic self-signing of GCS URLs (IAM `signBlob` API) under serverless ADC. |
| **Resource Manager API** | `cloudresourcemanager.googleapis.com` | Managing IAM Policy Bindings and service account roles with least privilege. |
| **Identity-Aware Proxy API** | `iap.googleapis.com` | Gating the web app behind Google login (`roles/iap.httpsResourceAccessor`) instead of public access. Enabled automatically by Terraform. |

---

## ⚡ Quick Start: Enable All APIs in 1-Second

Instead of navigating the Google Cloud Console UI web menus, you can enable all of the required APIs at once by executing this single, secure command in your terminal:

```bash
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  datastore.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  scheduler.googleapis.com \
  bigquery.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iap.googleapis.com \
  --project=YOUR_GCP_PROJECT_ID
```

---

## 📁 Directory Layout

*   📂 **`/environments`**: Contains environment-specific values (`/dev` and `/prod`) where the main state backends are located.
*   📂 **`/modules`**: Reusable infrastructure components:
    *   📂 **`/compute`**: Configures the serverless Cloud Run Service & Job.
    *   📂 **`/iam`**: Sets up dedicated Service Accounts and roles.
    *   📂 **`/scheduler`**: Deploys the automated Cron trigger.
    *   📂 **`/storage`**: Provisions the secure private GCS Audio bucket.
