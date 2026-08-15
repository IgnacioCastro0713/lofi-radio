import os
import datetime
import random
import io
import time
from mutagen.mp3 import MP3

from config import PROJECT_ID, BUCKET_NAME, TRACK_COUNT, ai_client
import generator
import gcs
import assembler

def main():
    print(f"=========================================================")
    print(f"Starting Modular Python Music Generator Worker")
    print(f"=========================================================")

    # Generate 4 daily pixel art images (one for each of the four moods)
    print("\n--- [Main] Generating 4 Daily AI Pixel Art Mood Images ---")
    for mood in ["day", "evening", "night", "pixel"]:
        try:
            image_bytes = generator.generate_mood_image(mood)
            if image_bytes:
                gcs.upload_mood_image(image_bytes, mood)
        except Exception as e:
            print(f"[Main] Warning: Failed to generate daily image for '{mood}': {e}")

    # Generate balanced shuffled blocks of 5 songs per mood to ensure high-variety daily playlists
    total_blocks = (TRACK_COUNT + 4) // 5
    moods_pool = ["day", "evening", "night", "pixel"]
    shuffled_blocks = []
    for i in range(total_blocks):
        shuffled_blocks.append(moods_pool[i % 4])
    random.shuffle(shuffled_blocks)
    print(f"[Main] Daily shuffled block moods sequence: {shuffled_blocks}")

    print(f"[Main] Starting generation of {TRACK_COUNT} total loop tracks...")

    generated_tracks = []

    try:
        for i in range(TRACK_COUNT):
            next_seq = i + 1
            try:
                # 1. Generate the track audio, title, and mood
                audio_bytes, title, mood = generator.generate_single_track(next_seq, shuffled_blocks)
                
                # 2. Calculate exact audio duration using mutagen
                try:
                    audio_file = io.BytesIO(audio_bytes)
                    mp3 = MP3(audio_file)
                    duration_seconds = float(mp3.info.length)
                    print(f"[Main] Calculated exact MP3 duration: {duration_seconds:.2f} seconds")
                except Exception as ex:
                    print(f"[Main] Warning: Failed to parse exact MP3 duration ({ex}). Using default 180.0 seconds.")
                    duration_seconds = 180.0

                # 3. Upload the MP3 file to GCS folder with metadata
                file_name, audio_url = gcs.upload_track_audio(audio_bytes, title, mood, duration_seconds)

                # 4. Buffer the track metadata in memory
                track_metadata = {
                    "file_name": file_name,
                    "audio_url": audio_url,
                    "duration_seconds": duration_seconds,
                    "status": "queued",
                    "play_start_time": None,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                    "title": title,
                    "mood": mood,
                    "image_path": f"{file_name.split('/')[0]}/images/{mood}.webp"
                }
                generated_tracks.append(track_metadata)
                print(f"[Main] Buffered track '{title}' successfully. ({len(generated_tracks)}/{TRACK_COUNT})")
                
            except Exception as e:
                print(f"[Main] Error generating track {next_seq}: {e}")
                print("[Main] Gracefully halting generation loop to assemble with already successful tracks.")
                break

            # Proactive rate-limiting breathing buffer between successful track generations
            if i < TRACK_COUNT - 1:
                print("[Main] Waiting 5 seconds as a rate-limit breathing buffer...")
                time.sleep(5)

    except Exception as e:
        print(f"[Main] Generation loop interrupted by unexpected exception: {e}")

    # 5. Assembler Phase: Dynamically rebuilds the contiguous playlist from the last 2 folders
    assembler.assemble_contiguous_sequence(generated_tracks)
    print("\n=========================================================")
    print("[Main] Modular Python Worker execution completed.")
    print("=========================================================")

if __name__ == "__main__":
    main()
