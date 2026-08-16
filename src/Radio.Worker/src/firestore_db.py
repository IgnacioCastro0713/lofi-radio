from config import db, PROJECT_ID

tracks_ref = db.collection("radio_tracks")

def wipe_tracks_collection():
    """
    Wipes all existing documents inside the 'radio_tracks' collection using BulkWriter.
    Optimized for high-throughput parallel asynchronous deletions.
    """
    try:
        all_current_docs = list(tracks_ref.list_documents())
        if not all_current_docs:
            print("[Firestore] Collection was already empty.")
            return
            
        print(f"[Firestore] Wiping existing Firestore collection 'radio_tracks' ({len(all_current_docs)} docs) using BulkWriter...")
        bulk_writer = db.bulk_writer()
        for doc in all_current_docs:
            bulk_writer.delete(doc)
            
        bulk_writer.close()
        print(f"[Firestore] Collection wiped successfully via BulkWriter ({len(all_current_docs)} docs).")
    except Exception as e:
        print(f"[Firestore] Error wiping collection: {e}")
        raise e

def save_contiguous_playlist(tracks_to_save):
    """
    Saves a list of track metadata dicts sequentially to Firestore with indexes 1 to N.
    Optimized using Firestore's native BulkWriter for high-throughput parallel asynchronous writes.
    """
    print(f"[Firestore] Saving {len(tracks_to_save)} contiguous tracks to Firestore using BulkWriter...")
    try:
        # Create a BulkWriter instance to handle parallel writes keylessly and auto-manage chunk/rate limits
        bulk_writer = db.bulk_writer()
        
        for idx, track_data in enumerate(tracks_to_save):
            seq = idx + 1
            track_data["sequence_index"] = seq
            
            doc_ref = tracks_ref.document(str(seq))
            track_data["id"] = doc_ref.id
            
            # Queue the write operation asynchronously
            bulk_writer.set(doc_ref, track_data)
            
        # Block and wait for all queued writes to complete
        bulk_writer.close()
        print("[Firestore] Playlist committed successfully via BulkWriter!")
    except Exception as e:
        print(f"[Firestore] Error saving contiguous playlist: {e}")
        raise e
