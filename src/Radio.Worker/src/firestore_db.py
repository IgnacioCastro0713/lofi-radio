from config import db, PROJECT_ID

tracks_ref = db.collection("radio_tracks")

def wipe_tracks_collection():
    """
    Wipes all existing documents inside the 'radio_tracks' collection using batch deletes.
    """
    print("[Firestore] Wiping existing Firestore collection 'radio_tracks'...")
    try:
        all_current_docs = list(tracks_ref.list_documents())
        if not all_current_docs:
            print("[Firestore] Collection was already empty.")
            return
            
        batch = db.batch()
        for doc in all_current_docs:
            batch.delete(doc)
        batch.commit()
        print("[Firestore] Collection wiped successfully.")
    except Exception as e:
        print(f"[Firestore] Error wiping collection: {e}")
        raise e

def save_contiguous_playlist(tracks_to_save):
    """
    Saves a list of track metadata dicts sequentially to Firestore with indexes 1 to N.
    """
    print(f"[Firestore] Saving {len(tracks_to_save)} contiguous tracks to Firestore...")
    try:
        for idx, track_data in enumerate(tracks_to_save):
            seq = idx + 1
            track_data["sequence_index"] = seq
            
            doc_ref = tracks_ref.document(str(seq))
            track_data["id"] = doc_ref.id
            
            doc_ref.set(track_data)
            print(f"[Firestore] Seq: {seq} | File: {track_data.get('file_name')} | Title: {track_data.get('title')}")
            
        print("[Firestore] Playlist committed successfully!")
    except Exception as e:
        print(f"[Firestore] Error saving contiguous playlist: {e}")
        raise e
