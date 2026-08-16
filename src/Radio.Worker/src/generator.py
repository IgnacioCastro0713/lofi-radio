import io
import random
import time
import base64
from PIL import Image
from google.genai import types
from config import ai_client, MUSIC_MODEL, IMAGE_MODEL
from prompts_data import TITLE_WORDS, TITLE_SUFFIXES, AUDIO_TEMPOS, AUDIO_GENRES, AUDIO_ELEMENTS, VISUAL_ELEMENTS, VISUAL_TEMPLATES, AUDIO_TEMPLATES

def determine_mood(next_seq, shuffled_blocks):
    """Determine the block index (0-based) for this sequence index"""
    block_index = (next_seq - 1) // 5
    if block_index >= len(shuffled_blocks):
        block_index = block_index % len(shuffled_blocks)
    return shuffled_blocks[block_index]

def generate_title(mood):
    """Generate a random, highly-varied, mood-appropriate title from TITLE_WORDS and TITLE_SUFFIXES database"""
    if mood not in TITLE_WORDS or mood not in TITLE_SUFFIXES:
        mood = "day"
        
    words = TITLE_WORDS[mood]
    suffixes = TITLE_SUFFIXES[mood]
    
    base_title = f"{random.choice(words['adj'])} {random.choice(words['noun'])}"
    # 70% probability to append a gorgeous location/time suffix (creates 168,000+ combinations!)
    if random.random() < 0.70:
        title = f"{base_title} {random.choice(suffixes)}"
        return title.title()
        
    return base_title.title()

def get_prompt_for_mood(mood, title):
    """Generate a randomized compliant descriptive prompt for Vertex AI Lyria using dynamic structural templates"""
    if mood not in AUDIO_ELEMENTS or mood not in AUDIO_GENRES:
        mood = "day"
        
    tempo = random.choice(AUDIO_TEMPOS)
    elem = AUDIO_ELEMENTS[mood]
    
    # Randomly select one of the four unique audio prompt template styles
    template = random.choice(AUDIO_TEMPLATES)
    
    # Dynamically select randomized genre and theme template
    # All lofi genres are strictly defined as relaxing, warm, cozy, and soothing!
    genre_data = random.choice(AUDIO_GENRES[mood])
    genre_desc = genre_data["genre"]
    theme_desc = genre_data["theme"]
    
    vars_dict = {
        "genre_desc": genre_desc,
        "theme_desc": theme_desc,
        "tempo": tempo,
        "harmonies": random.choice(elem["harmonies"]),
        "instruments": random.choice(elem["instruments"]),
        "beats": random.choice(elem["beats"]),
        "textures": random.choice(elem["textures"]),
        "title": title
    }
        
    return template.format(**vars_dict)

def generate_single_track(next_seq, shuffled_blocks):
    """
    Assembles prompt, calls Google Vertex AI Lyria 3, and returns decoded raw audio bytes 
    along with metadata. Handles retries internally. Falls back to a high-quality mock
    silent track on persistent quota/rate-limit failures.
    """
    max_prompt_retries = 5
    mood = determine_mood(next_seq, shuffled_blocks)
    title = generate_title(mood)

    for prompt_attempt in range(max_prompt_retries):
        # Regenerate title on each retry attempt to bypass any blocked title keywords!
        if prompt_attempt > 0:
            title = generate_title(mood)
            
        prompt = get_prompt_for_mood(mood, title)

        if prompt_attempt == 0:
            print(f"[Generator] Generating track {next_seq} ('{title}' - [{mood}]) with {MUSIC_MODEL}...")
        else:
            print(f"[Generator] Retrying track {next_seq} with fresh prompt ('{title}' - [{mood}]) [Attempt {prompt_attempt+1}/{max_prompt_retries}]...")

        # Resilient network call retry loop
        max_network_retries = 3
        retry_delay = 5
        interaction = None
        is_blocked = False

        for attempt in range(max_network_retries):
            try:
                interaction = ai_client.interactions.create(
                    model=MUSIC_MODEL,
                    input=prompt
                )
                break
            except Exception as e:
                err_msg = str(e).lower()
                if "content_blocked" in err_msg or "policy" in err_msg or "blocked" in err_msg:
                    print(f"[Generator] Warning: Prompt was blocked by safety policies: {e}")
                    is_blocked = True
                    break # Break network loop immediately to generate a new prompt
                
                if attempt < max_network_retries - 1:
                    print(f"[Generator] Warning: Network attempt {attempt+1} failed: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"[Generator] Error: All network attempts failed for track {next_seq}.")
                    raise e

        if is_blocked:
            continue # Try next prompt attempt

        # Parse AI response audio payload
        try:
            audio_bytes = None
            if interaction:
                if getattr(interaction, "outputs", None):
                    for out_block in interaction.outputs:
                        if getattr(out_block, "type", None) == "audio" and getattr(out_block, "data", None):
                            audio_bytes = out_block.data
                            break
                elif getattr(interaction, "steps", None):
                    for step in interaction.steps:
                        if getattr(step, "type", None) == "model_output" and getattr(step, "content", None):
                            for out_block in step.content:
                                if getattr(out_block, "type", None) == "audio" and getattr(out_block, "data", None):
                                    audio_bytes = out_block.data
                                    break

            if audio_bytes:
                if isinstance(audio_bytes, str):
                    audio_bytes = base64.b64decode(audio_bytes)
                return audio_bytes, title, mood
            else:
                print("[Generator] Error: Response did not contain audio data.")
        except Exception as e:
            print(f"[Generator] Exception parsing response for track {next_seq}: {e}")
            continue

    # Resilient Self-Healing Fallback: If Lyria is rate-limited (429) or fails, return a synthetic mock track
    print(f"[Generator] Warning: Lyria 3 failed or rate limit exhausted. Falling back to a synthetic mock track to prevent pipeline crash.")
    mock_audio = base64.b64decode(
        "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGFtZTMuOTguNAAAAAAAAAAAAAAA"
        "//uQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtMYW1l"
        "My45OC40VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//uQ"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVVVVVVVVVV"
        "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    )
    return mock_audio, f"{title} (MOCK)", mood

def generate_dynamic_image_prompt(mood):
    """
    Dynamically assembles a unique 16-bit visual prompt
    based on randomized style templates and randomized visual elements.
    """
    if mood not in VISUAL_ELEMENTS or mood not in VISUAL_TEMPLATES:
        mood = "day"
        
    elem = VISUAL_ELEMENTS[mood]
    templates = VISUAL_TEMPLATES[mood]
    template = random.choice(templates)
    
    if mood == "day":
        vars_dict = {
            "obj": random.choice(elem["desk_objects"]),
            "view": random.choice(elem["window_views"]),
            "amb": random.choice(elem["ambience"]),
            "palette": random.choice(elem["palettes"])
        }
    elif mood == "evening":
        vars_dict = {
            "obj": random.choice(elem["table_objects"]),
            "view": random.choice(elem["window_views"]),
            "amb": random.choice(elem["ambience"])
        }
    elif mood == "night":
        vars_dict = {
            "sky": random.choice(elem["sky_views"]),
            "light": random.choice(elem["light_sources"]),
            "amb": random.choice(elem["ambience"])
        }
    elif mood == "pixel":
        vars_dict = {
            "console": random.choice(elem["consoles"]),
            "screen": random.choice(elem["screen_content"]),
            "bg": random.choice(elem["backgrounds"])
        }
    elif mood == "synthwave":
        vars_dict = {
            "vehicle": random.choice(elem["vehicles"]),
            "sun": random.choice(elem["suns"]),
            "bg": random.choice(elem["backgrounds"])
        }
    else:
        return "detailed 16-bit lofi style pixel art, 16:9 widescreen format"
        
    return template.format(**vars_dict)

def generate_mood_image(mood):
    """
    Generates a beautiful lofi pixel art image using gemini-3.1-flash-image
    corresponding to the specified mood globally. The image is generated natively
    and then programmatically converted to WebP in memory to guarantee lightweight transmission.
    """
    prompt = generate_dynamic_image_prompt(mood)
    print(f"[Generator] Generating daily pixel art image for mood '{mood}' using {IMAGE_MODEL}..."
    )
    
    try:
        response = ai_client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )
        
        # Extract image bytes
        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break
                
        if image_bytes:
            if isinstance(image_bytes, str):
                image_bytes = base64.b64decode(image_bytes)
                
            # Perform programmatic WebP conversion using local Pillow library
            try:
                img = Image.open(io.BytesIO(image_bytes))
                webp_io = io.BytesIO()
                img.save(webp_io, format="WEBP", quality=80)
                image_bytes = webp_io.getvalue()
                print(f"[Generator] Programmatically converted image to WebP in memory.")
            except Exception as conv_ex:
                print(f"[Generator] Warning: Failed to convert image to WebP ({conv_ex}). Uploading raw bytes as fallback.")
                
            print(f"[Generator] Successfully generated daily image for mood '{mood}' (Size: {len(image_bytes)} bytes)")
            return image_bytes
        else:
            print(f"[Generator] Error: Response did not contain inline image data.")
            return None
    except Exception as e:
        print(f"[Generator] Error generating image for mood '{mood}': {e}")
        return None
