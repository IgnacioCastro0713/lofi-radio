import os
import uuid
import datetime
import random
import base64
import io
import time
from google.cloud import firestore
from google.cloud import storage
import google.genai as genai
from mutagen.mp3 import MP3

def determine_mood(next_seq, shuffled_blocks):
    # Determine the block index (0-based) for this sequence index
    block_index = (next_seq - 1) // 5
    
    # Safety bounds check
    if block_index >= len(shuffled_blocks):
        block_index = block_index % len(shuffled_blocks)
        
    return shuffled_blocks[block_index]

# Cozy adverbs and nouns matching C# logic
day_adj = ["Sunny", "Pixel", "Focus", "Cozy", "Desk", "Morning", "Warm", "Coffee", "Fresh", "Bright"]
day_noun = ["Terminal", "Keys", "Chords", "Workspace", "Keyboard", "Window", "Code", "Beat", "Vibes", "Mug"]

evening_adj = ["Sunset", "Golden", "Mellow", "Subway", "Orange", "Cozy", "Rainy", "Chill", "Velvet", "Dreamy"]
evening_noun = ["Station", "Dream", "Saxo", "Beat", "Train", "Avenue", "Lounge", "Smoke", "Shadows", "Vibes"]

night_adj = ["Midnight", "Neon", "Cyberpunk", "Deep", "Dreamy", "Silent", "Purple", "Starry", "Rainy", "Velvet"]
night_noun = ["Hum", "Memory", "Rain", "Sub", "Lullaby", "Star", "Computer", "Sleeper", "Echo", "Glow"]

pixel_adj = ["8-Bit", "Chiptune", "Retro", "Pixel", "Arcade", "Glitch", "Console", "Level", "Vintage", "Handheld"]
pixel_noun = ["Castle", "Dungeon", "Quest", "Hero", "Sprites", "Savepoint", "Cartridge", "Screen", "Forest", "Heart"]

def generate_title(mood):
    if mood == "evening":
        return f"{random.choice(evening_adj)} {random.choice(evening_noun)}"
    elif mood == "night":
        return f"{random.choice(night_adj)} {random.choice(night_noun)}"
    elif mood == "pixel":
        return f"{random.choice(pixel_adj)} {random.choice(pixel_noun)}"
    else:
        return f"{random.choice(day_adj)} {random.choice(day_noun)}"

def get_prompt_for_mood(mood, title):
    # Pools of creative variations to ensure infinite musical variety, distinct atmospheres,
    # and to guarantee 100% safety filter compliance by avoiding repetitive structures!
    tempos = ["slow-paced 72 BPM", "relaxed 76 BPM", "laid-back 80 BPM", "mellow 84 BPM"]
    tempo = random.choice(tempos)
    
    if mood == "day":
        instruments = [
            "warm electric piano and soft acoustic guitar",
            "mellow Rhodes keys and clean Fender Stratocaster riffs",
            "organic kalimba arpeggios and nostalgic muted guitar",
            "cozy Wurlitzer chords and a soft nylon-string guitar"
        ]
        beats = [
            "dusty lofi boom-bap drums",
            "relaxed lofi hip hop swing beats",
            "laid-back organic percussion"
        ]
        textures = [
            "soft vinyl crackle and distant morning birds",
            "cozy coffee shop background room-tone",
            "gentle breeze rustling through open windows"
        ]
        return (
            f"A peaceful and highly focused {mood} lofi hip hop track at a {tempo}. "
            f"Featuring {random.choice(instruments)}, accompanied by {random.choice(beats)}, "
            f"and wrapped in {random.choice(textures)}. Purely instrumental, no vocals. "
            f"Inspired by the cozy theme: '{title}'."
        )
    elif mood == "evening":
        instruments = [
            "jazzy electric guitar chords and a smooth soulful saxophone lead",
            "warm hollow-body jazz guitar and a mellow muted trumpet",
            "relaxed jazz-hop piano chords and a soft acoustic double bass",
            "cozy jazz piano and a warm, breathy tenor saxophone melody"
        ]
        beats = [
            "slow-paced jazzy lofi snare and brush drums",
            "relaxed dusty hip hop drum swing",
            "mellow organic rimshots and laid-back snare beats"
        ]
        textures = [
            "a soft crackling fireplace in the background",
            "gentle evening rain on a glass window",
            "warm, dusty vinyl record noise"
        ]
        return (
            f"A warm, relaxing, and soulful {mood} jazzhop lofi track at a {tempo}. "
            f"Featuring {random.choice(instruments)}, over {random.choice(beats)}, "
            f"with {random.choice(textures)}. Purely instrumental, no vocals. "
            f"Inspired by the cozy theme: '{title}'."
        )
    elif mood == "night":
        instruments = [
            "soft reverbed piano and slow ambient synthesizer pads",
            "ultra-mellow Rhodes keys and a warm, breathing sub-bass",
            "dreamy celesta bells and gentle sweeping ambient textures",
            "soft, distant electric piano chords and slow-evolving spacey pads"
        ]
        beats = [
            "extremely slow-paced lofi brush beats",
            "minimalist dusty kick and rimshot",
            "a very gentle, laid-back low-pass filtered drum track"
        ]
        textures = [
            "gentle, steady rain falling on a Tokyo street",
            "soft, rhythmic waves lapping on a quiet night beach",
            "warm analog tape hiss and a cozy room ambiance"
        ]
        return (
            f"An ultra-mellow, dreamy, and peaceful {mood} sleep lofi track at a {tempo}. "
            f"Featuring {random.choice(instruments)}, layered over {random.choice(beats)}, "
            f"accompanied by {random.choice(textures)}. Purely instrumental, no vocals. "
            f"Inspired by the cozy theme: '{title}'."
        )
    else: # pixel (Retro / Chiptune)
        instruments = [
            "vintage 8-bit square-wave leads and nostalgic NES 2A03 triangle-wave bass",
            "playful 16-bit FM-synthesis chords and retro Game Boy PSG melodies",
            "warm retro game-console synth arpeggios and nostalgic 8-bit chords",
            "pixelated sound chip square-wave melodies and a soft vintage synthesizer lead"
        ]
        beats = [
            "relaxing lofi hip hop drum beats with a 12-bit crunch",
            "mellow dusty organic chip-drums",
            "laid-back organic chiptune-inspired snare swing"
        ]
        textures = [
            "playful retro game start bleeps and soft pixelated sound effects",
            "warm retro game-room room-tone and soft analog console noise",
            "cozy low-fidelity 8-bit sound-effects and gentle static"
        ]
        return (
            f"A cozy and highly nostalgic 8-bit chiptune {mood} lofi track at a {tempo}. "
            f"Featuring {random.choice(instruments)}, accompanied by {random.choice(beats)}, "
            f"and seasoned with {random.choice(textures)}. Purely instrumental, no vocals. "
            f"Inspired by the retro game theme: '{title}'."
        )

def main():
    project_id = os.getenv("GCP_PROJECT_ID")
    bucket_name = os.getenv("GCS_BUCKET_NAME")

    print(f"Starting Python Music Generator Worker for Project: {project_id}")
    print(f"Target GCS Bucket: {bucket_name}")

    db = firestore.Client(project=project_id)
    storage_client = storage.Client(project=project_id)
    
    # Initialize the Google GenAI Client in Vertex AI mode
    # This instructs the SDK to use native Google Cloud IAM (Service Account Application Default Credentials) keylessly!
    ai_client = genai.Client(
        vertexai=True,
        project=project_id,
        location="global"
    )

    tracks_ref = db.collection("radio_tracks")

    # In-Place Overwrite Pattern: No initial purging of GCS or Firestore is performed.
    # Newly generated tracks will dynamically overwrite the existing 100 document slots in-place
    # during generation. This keeps your daily radio 100% online and prevents any catastrophic
    # data-wiping loop if Vertex AI experiences temporary latency!

    TRACK_COUNT = int(os.getenv("TRACK_COUNT", "100"))
    print(f"Dynamic loop track count configured at: {TRACK_COUNT} tracks")

    # Generate balanced shuffled blocks of 5 songs per mood to ensure high-variety daily playlists
    total_blocks = (TRACK_COUNT + 4) // 5
    moods_pool = ["day", "evening", "night", "pixel"]
    shuffled_blocks = []
    for i in range(total_blocks):
        shuffled_blocks.append(moods_pool[i % 4])
    random.shuffle(shuffled_blocks)
    print(f"Daily shuffled block moods sequence: {shuffled_blocks}")

    print(f"Generating {TRACK_COUNT} total loop tracks sequentially...")

    for i in range(TRACK_COUNT):
        next_seq = 1 + i
        generation_success = False
        max_prompt_retries = 5

        for prompt_attempt in range(max_prompt_retries):
            mood = determine_mood(next_seq, shuffled_blocks)
            title = generate_title(mood)
            prompt = get_prompt_for_mood(mood, title)

            if prompt_attempt == 0:
                print(f"[{i+1}/{TRACK_COUNT}] Generating track {next_seq} ('{title}' - [{mood}]) with Lyria 3 Pro...")
            else:
                print(f"[{i+1}/{TRACK_COUNT}] Retrying track {next_seq} with fresh theme ('{title}' - [{mood}]) [Attempt {prompt_attempt+1}/{max_prompt_retries}]...")

            # Call Interactions API with a resilient retry loop to handle transient network issues or rate limits
            max_network_retries = 3
            retry_delay = 5
            interaction = None
            is_blocked = False

            for attempt in range(max_network_retries):
                try:
                    interaction = ai_client.interactions.create(
                        model="lyria-3-pro-preview",
                        input=prompt
                    )
                    break
                except Exception as e:
                    # Check if the error is a content blocked or BadRequest safety filter exception
                    err_msg = str(e).lower()
                    if "content_blocked" in err_msg or "policy" in err_msg or "blocked" in err_msg:
                        print(f"Warning: Prompt for track {next_seq} was blocked by safety filters: {e}")
                        is_blocked = True
                        break # break the network loop immediately to regenerate a new prompt!
                    
                    if attempt < max_network_retries - 1:
                        print(f"Warning: Network attempt {attempt+1} failed: {e}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"Error: All network attempts failed for track {next_seq}.")
                        raise e

            if is_blocked:
                # Loop back to generate a completely new random title and prompt!
                continue

            try:
                # Parse the response dynamically to support both v1.x (outputs) and v2.x (steps) SDK schemas!
                audio_bytes = None
                
                if interaction:
                    if getattr(interaction, "outputs", None):
                        # v1.x SDK parsing schema
                        for out_block in interaction.outputs:
                            if getattr(out_block, "type", None) == "audio" and getattr(out_block, "data", None):
                                audio_bytes = out_block.data
                                break
                    elif getattr(interaction, "steps", None):
                        # v2.x SDK parsing schema (steps -> model_output -> content -> audio)
                        for step in interaction.steps:
                            if getattr(step, "type", None) == "model_output" and getattr(step, "content", None):
                                for out_block in step.content:
                                    if getattr(out_block, "type", None) == "audio" and getattr(out_block, "data", None):
                                        audio_bytes = out_block.data
                                        break

                if audio_bytes:
                    # Decode Base64 audio string to raw bytes
                    if isinstance(audio_bytes, str):
                        audio_bytes = base64.b64decode(audio_bytes)

                    # Upload to GCS
                    file_name = f"{uuid.uuid4().hex}.mp3"
                    
                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(file_name)
                    blob.upload_from_string(audio_bytes, content_type="audio/mp3")
                    print(f"Uploaded successfully to GCS: {file_name}")

                    # Align metadata with C# CloudStorageService expectations
                    audio_url = f"https://storage.cloud.google.com/{bucket_name}/{file_name}"
                    
                    # Calculate the microsecond-exact duration of the generated MP3 using Mutagen
                    try:
                        audio_file = io.BytesIO(audio_bytes)
                        mp3 = MP3(audio_file)
                        duration_seconds = float(mp3.info.length)
                        print(f"Calculated exact MP3 duration: {duration_seconds:.2f} seconds")
                    except Exception as ex:
                        print(f"Warning: Failed to parse exact MP3 duration ({ex}). Using default 180.0 seconds.")
                        duration_seconds = 180.0

                    # Write record to Firestore using the exact sequence index as the Document ID (In-Place Overwrite Pattern)
                    doc_ref = tracks_ref.document(str(next_seq))
                    doc_ref.set({
                        "id": doc_ref.id,
                        "file_name": file_name,
                        "audio_url": audio_url,
                        "duration_seconds": duration_seconds,
                        "sequence_index": next_seq,
                        "status": "queued",
                        "play_start_time": None,
                        "created_at": datetime.datetime.now(datetime.timezone.utc),
                        "title": title,
                        "mood": mood
                    })
                    print(f"Saved track metadata to Firestore successfully!")
                    generation_success = True
                    break # Break the prompt_attempt loop! We succeeded!
                else:
                    print("Error: Interaction response did not contain audio data.")
            except Exception as e:
                print(f"Failed to process track {next_seq} during this attempt: {e}")
                # We can retry
                continue

        if not generation_success:
            raise RuntimeError(f"Error: Failed to generate track {next_seq} after {max_prompt_retries} self-healing prompt variations.")

        # Proactive rate-limiting breathing buffer (5 seconds) between successful track generations
        if i < TRACK_COUNT - 1:
            print("Waiting 5 seconds as a rate-limit breathing buffer...")
            time.sleep(5)

    print("Cushion generation completed successfully!")

if __name__ == "__main__":
    main()
