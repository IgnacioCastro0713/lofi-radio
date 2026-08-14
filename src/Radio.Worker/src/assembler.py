import datetime
import gcs
import firestore_db
from config import BUCKET_NAME

def assemble_contiguous_sequence(generated_tracks=None):
    """
    Scans the GCS bucket to find the last 2 YYYYMMDD date folders, pulls their files,
    reads their custom object metadata (title, mood, duration_seconds) directly from GCS,
    rebuilds a contiguous 1 to N playlist sequence, and saves it to Firestore.
    """
    print("\n=== [Assembler] Rebuilding Playlist from Last 2 Folders ===")
    
    try:
        # 1. List GCS blobs and identify YYYYMMDD folders
        all_blobs = gcs.list_bucket_blobs()
        
        folder_blobs = {}
        for blob in all_blobs:
            parts = blob.name.split('/')
            if len(parts) == 2:
                folder = parts[0]
                # Check if matches compact YYYYMMDD pattern (8 digits)
                if len(folder) == 8 and folder.isdigit():
                    if folder not in folder_blobs:
                        folder_blobs[folder] = []
                    folder_blobs[folder].append(blob)
                    
        # Sort folders chronologically/alphabetically
        sorted_folders = sorted(folder_blobs.keys())
        print(f"[Assembler] Discovered folders in bucket: {sorted_folders}")
        
        if not sorted_folders:
            print("[Assembler] No valid date folders found in GCS bucket. Skipping.")
            return
            
        # Select the last 2 folders
        folders_to_keep = sorted_folders[-2:]
        print(f"[Assembler] Selecting the last 2 folders: {folders_to_keep}")
        
        # Gap-check: If there is a weekend or holiday gap (> 1 day), discard the older folder
        # to prevent streaming files that are scheduled to be deleted mid-day by GCS lifecycle rules.
        if len(folders_to_keep) == 2:
            try:
                date_format = "%Y%m%d"
                date_a = datetime.datetime.strptime(folders_to_keep[0], date_format)
                date_b = datetime.datetime.strptime(folders_to_keep[1], date_format)
                delta_days = (date_b - date_a).days
                if delta_days > 1:
                    print(f"[Assembler] Detected gap of {delta_days} days between {folders_to_keep[0]} and {folders_to_keep[1]} (e.g., weekend).")
                    print(f"[Assembler] Discarding older folder {folders_to_keep[0]} to avoid mid-day GCS lifecycle deletions.")
                    folders_to_keep = [folders_to_keep[1]]
            except Exception as e:
                print(f"[Assembler] Warning: Failed to parse folder date gap check: {e}")
        
        # Sort folders descending so newest folders are listed first (e.g. today's first, yesterday's second)
        folders_to_keep_sorted = sorted(folders_to_keep, reverse=True)
        
        # 2. Collect blobs from these 2 folders
        blobs_to_keep = []
        for folder in folders_to_keep_sorted:
            blobs_in_folder = sorted(folder_blobs[folder], key=lambda b: b.name)
            blobs_to_keep.extend(blobs_in_folder)
            
        print(f"[Assembler] Total files collected from last 2 folders: {len(blobs_to_keep)}")
        
        if not blobs_to_keep:
            print("[Assembler] No files found in selected folders. Skipping.")
            return

        # 3. Resolve metadata and prepare list to save
        tracks_to_save = []
        for blob in blobs_to_keep:
            file_name = blob.name
            
            # Read custom GCS object metadata
            metadata = blob.metadata or {}
            title = metadata.get("title")
            mood = metadata.get("mood")
            duration_str = metadata.get("duration_seconds")
            image_path = metadata.get("image_path")
            
            # Fallback if metadata is missing (e.g., manually uploaded files)
            if not title:
                parts = file_name.split('/')
                title = parts[1].replace(".mp3", "") if len(parts) == 2 else file_name
            if not mood:
                mood = "day"
            if not image_path:
                image_path = f"{file_name.split('/')[0]}/images/{mood}.webp"
            
            try:
                duration_seconds = float(duration_str) if duration_str else 180.0
            except ValueError:
                duration_seconds = 180.0
                
            # Use GCS blob creation time as the timestamp
            created_at = blob.time_created or datetime.datetime.now(datetime.timezone.utc)
            audio_url = f"https://storage.cloud.google.com/{BUCKET_NAME}/{file_name}"
            
            tracks_to_save.append({
                "file_name": file_name,
                "audio_url": audio_url,
                "duration_seconds": duration_seconds,
                "created_at": created_at,
                "title": title,
                "mood": mood,
                "image_path": image_path
            })
            
        # 4. Clear Firestore and save contiguous list
        firestore_db.wipe_tracks_collection()
        firestore_db.save_contiguous_playlist(tracks_to_save)
        
        print(f"\n=== [Assembler] Playlist assembled successfully with {len(tracks_to_save)} tracks! ===")

    except Exception as e:
        print(f"[Assembler] Error during sequence assembly: {e}")
        raise e
