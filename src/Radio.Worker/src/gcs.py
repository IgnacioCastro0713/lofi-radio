import os
import uuid
import datetime
from config import storage_client, BUCKET_NAME

def upload_track_audio(audio_bytes, title, mood, duration_seconds):
    """
    Uploads raw audio bytes to a YYYYMMDD prefixed folder in GCS with custom metadata.
    Supports a SIMULATED_DATE environment variable for testing/simulation.
    Returns the virtual file name (object name) and public url.
    """
    sim_date = os.getenv("SIMULATED_DATE")
    if sim_date:
        current_date = sim_date
        print(f"[GCS] Using simulated date folder: {current_date}")
    else:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        
    file_name = f"{current_date}/{uuid.uuid4().hex}.mp3"
    
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    
    # Set custom object metadata
    # Format Example: "2026-08-15" (YYYY-MM-dd UTC date string)
    created_at_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    image_path = f"{current_date}/images/{mood}.webp"
    blob.metadata = {
        "title": title,
        "mood": mood,
        "duration_seconds": str(duration_seconds),
        "image_path": image_path,
        "created_at_utc": created_at_utc
    }
    
    blob.upload_from_string(audio_bytes, content_type="audio/mp3")
    
    print(f"[GCS] Uploaded successfully to bucket with metadata: {file_name}")
    audio_url = f"https://storage.cloud.google.com/{BUCKET_NAME}/{file_name}"
    
    return file_name, audio_url, created_at_utc

def list_bucket_blobs():
    """
    Retrieves all blobs present in the configured GCS bucket with full metadata projection
    so custom metadata is retrieved in a single batch list call.
    """
    bucket = storage_client.bucket(BUCKET_NAME)
    return list(bucket.list_blobs(projection="full"))

def upload_mood_image(image_bytes, mood):
    """
    Uploads raw PNG/JPEG bytes to the YYYYMMDD/images/ folder as mood.png.
    Supports a SIMULATED_DATE environment variable for testing/simulation.
    """
    sim_date = os.getenv("SIMULATED_DATE")
    if sim_date:
        current_date = sim_date
        print(f"[GCS] Using simulated date folder for image: {current_date}")
    else:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        
    file_name = f"{current_date}/images/{mood}.webp"
    
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(image_bytes, content_type="image/webp")
    
    print(f"[GCS] Uploaded daily mood image successfully: {file_name}")
    return file_name
