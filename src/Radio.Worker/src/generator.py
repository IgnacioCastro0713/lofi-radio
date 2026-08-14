import io
import random
import time
import base64
from PIL import Image
from google.genai import types
from config import ai_client

# Mood theme datasets
day_adj = ["Sunny", "Pixel", "Focus", "Cozy", "Desk", "Morning", "Warm", "Coffee", "Fresh", "Bright"]
day_noun = ["Terminal", "Keys", "Chords", "Workspace", "Keyboard", "Window", "Code", "Beat", "Vibes", "Mug"]

evening_adj = ["Sunset", "Golden", "Mellow", "Twilight", "Orange", "Cozy", "Rainy", "Chill", "Velvet", "Dreamy"]
evening_noun = ["Station", "Dream", "Saxo", "Beat", "Train", "Avenue", "Lounge", "Steam", "Shadows", "Vibes"]

night_adj = ["Midnight", "Neon", "Cosmic", "Deep", "Dreamy", "Silent", "Purple", "Starry", "Rainy", "Velvet"]
night_noun = ["Hum", "Memory", "Rain", "Waves", "Lullaby", "Star", "Computer", "Sleeper", "Echo", "Glow"]

pixel_adj = ["8-Bit", "Chiptune", "Retro", "Pixel", "Arcade", "Glitch", "Console", "Level", "Vintage", "Handheld"]
pixel_noun = ["Castle", "Dungeon", "Quest", "Hero", "Sprites", "Savepoint", "Cartridge", "Screen", "Forest", "Heart"]

def determine_mood(next_seq, shuffled_blocks):
    """Determine the block index (0-based) for this sequence index"""
    block_index = (next_seq - 1) // 5
    if block_index >= len(shuffled_blocks):
        block_index = block_index % len(shuffled_blocks)
    return shuffled_blocks[block_index]

def generate_title(mood):
    """Generate a random mood-appropriate title"""
    if mood == "evening":
        return f"{random.choice(evening_adj)} {random.choice(evening_noun)}"
    elif mood == "night":
        return f"{random.choice(night_adj)} {random.choice(night_noun)}"
    elif mood == "pixel":
        return f"{random.choice(pixel_adj)} {random.choice(pixel_noun)}"
    else:
        return f"{random.choice(day_adj)} {random.choice(day_noun)}"

def get_prompt_for_mood(mood, title):
    """Generate a randomized compliant descriptive prompt for Vertex AI Lyria"""
    tempos = ["slow-paced 72 BPM", "relaxed 76 BPM", "laid-back 80 BPM", "mellow 84 BPM"]
    tempo = random.choice(tempos)
    
    if mood == "day":
        instruments = [
            "warm electric piano and soft fingerstyle acoustic guitar",
            "mellow vintage electric keys and clean retro electric guitar riffs",
            "organic acoustic kalimba arpeggios, warm vintage electric keys, and a clean electric bass",
            "cozy vintage reed organ chords, clean electric guitar, and soft synthesized bells",
            "warm retro organ chords, soothing acoustic slide guitar, and a subtle electric piano",
            "smooth electric piano, light steel-string acoustic guitar, and soft vibraphone notes"
        ]
        beats = [
            "dusty lofi boom-bap drums with a gentle kick and soft snare",
            "relaxed lofi hip hop swing beats with a warm crackling rimshot",
            "laid-back organic acoustic percussion and a very soft kick-snare pattern",
            "chill down-tempo lofi drum loop with heavily filtered hi-hats",
            "soft shuffle drums and a warm, steady bassline"
        ]
        textures = [
            "soft vinyl crackle and distant morning birds singing",
            "cozy coffee shop background room-tone with faint chatter and cup clinks",
            "gentle morning breeze rustling through open windows",
            "subtle analog tape hiss and the warm sound of distant morning rain",
            "soft wind chimes and warm analog record dust noise"
        ]
        harmonies = [
            "in a warm major-seventh progression",
            "using cozy major chord structures",
            "in a peaceful, soothing major key center"
        ]
        return (
            f"A peaceful and highly focused {mood} lofi hip hop track at a {tempo}, "
            f"{random.choice(harmonies)}. Featuring {random.choice(instruments)}, "
            f"accompanied by {random.choice(beats)}, and wrapped in {random.choice(textures)}. "
            f"Purely instrumental, no vocals. Inspired by the cozy theme: '{title}'."
        )
    elif mood == "evening":
        instruments = [
            "jazzy electric guitar chords and a smooth soulful saxophone lead",
            "warm hollow-body jazz guitar and a mellow muted trumpet melody",
            "relaxed jazz-hop piano chords and a soft, warm acoustic double bass",
            "cozy jazz piano, a warm breathy tenor saxophone, and a light vibraphone",
            "mellow retro electric keys, a clean jazz hollow-body guitar, and a soft flute lead",
            "warm retro drawbar organ chords, smooth jazzy guitar riffs, and a mellow contrabass"
        ]
        beats = [
            "slow-paced jazzy lofi snare and brush drums",
            "relaxed dusty hip hop drum swing with a warm rimshot",
            "mellow organic rimshots, laid-back snare beats, and a swinging ride cymbal",
            "chill jazzy boom-bap rhythm with highly filtered, soft percussion",
            "smooth swing snare and brush drums with a warm, driving jazz beat"
        ]
        textures = [
            "a soft crackling fireplace in the background",
            "gentle evening rain tapping on a glass window",
            "warm, dusty vinyl record noise and faint street ambiance",
            "cozy evening cafe room-tone and a distant city hum",
            "analog tape saturation and soft wind rustling in the twilight"
        ]
        harmonies = [
            "in a jazzy minor-ninth chord progression",
            "using smooth, elegant jazz minor chords",
            "with sophisticated major-ninth and minor-ninth harmonies"
        ]
        return (
            f"A warm, relaxing, and soulful {mood} jazzhop lofi track at a {tempo}, "
            f"{random.choice(harmonies)}. Featuring {random.choice(instruments)}, "
            f"over {random.choice(beats)}, with {random.choice(textures)}. "
            f"Purely instrumental, no vocals. Inspired by the cozy theme: '{title}'."
        )
    elif mood == "night":
        instruments = [
            "soft reverbed piano and slow ambient synthesizer pads",
            "ultra-mellow vintage electric keys and a warm, breathing sub-bass",
            "dreamy celesta bells and gentle sweeping ambient textures",
            "soft, distant electric piano chords and slow-evolving spacey pads",
            "mellow glockenspiel notes, a very soft acoustic nylon guitar, and deep synth pads",
            "slow-moving reverbed vintage electric keys, soft ambient wave-like synths, and a deep bass hum"
        ]
        beats = [
            "extremely slow-paced lofi brush beats",
            "minimalist dusty kick and soft rimshot",
            "a very gentle, laid-back low-pass filtered drum track",
            "soft, slow-tempo organic heartbeat-like percussion",
            "no heavy drums, just an ultra-slow, breathing ambient synth pulse"
        ]
        textures = [
            "a gentle, steady rain falling on a quiet neon-lit city street",
            "soft, rhythmic waves lapping on a quiet night beach",
            "warm analog tape hiss and a cozy room ambiance",
            "gentle midnight crickets and a soft, warm summer breeze",
            "distant thunder claps and steady, soothing rain soundscapes"
        ]
        harmonies = [
            "in a slow-moving, heavily reverbed minor-seventh progression",
            "using deep, ambient minor chord structures",
            "in an ultra-soft, slow-evolving atmospheric progression"
        ]
        return (
            f"An ultra-mellow, dreamy, and peaceful {mood} sleep lofi track at a {tempo}, "
            f"{random.choice(harmonies)}. Featuring {random.choice(instruments)}, "
            f"layered over {random.choice(beats)}, accompanied by {random.choice(textures)}. "
            f"Purely instrumental, no vocals. Inspired by the cozy theme: '{title}'."
        )
    else: # pixel (Retro / Chiptune)
        instruments = [
            "vintage 8-bit square-wave leads and nostalgic retro game-console triangle-wave bass",
            "playful 16-bit FM-synthesis chords and retro handheld console square-wave melodies",
            "warm retro game-console synth arpeggios and nostalgic 8-bit pulse-wave chords",
            "pixelated sound chip square-wave melodies and a soft vintage synthesizer lead",
            "soft 8-bit pulse-wave chiptune leads, retro chord progressions, and a vintage game-synth pad",
            "nostalgic 16-bit soundcard piano chords, playful square-wave arpeggios, and low-passed retro bass"
        ]
        beats = [
            "relaxing lofi hip hop drum beats with a dusty 12-bit crunch",
            "mellow dusty organic chip-drums and soft retro game-console noise",
            "laid-back organic chiptune-inspired snare swing with a retro kick",
            "chill down-tempo 12-bit sampler drums with soft, bit-crushed hi-hats",
            "retro 8-bit arcade-style drum machine rhythm, low-passed and relaxed"
        ]
        textures = [
            "playful retro game start bleeps and soft pixelated sound effects",
            "warm retro game-room room-tone and soft analog console noise",
            "cozy low-fidelity 8-bit sound-effects and gentle static",
            "faint sounds of an old CRT television humming and retro arcade ambiance",
            "vintage 8-bit game pause sounds and warm cassette tape warble"
        ]
        harmonies = [
            "in a playful, retro minor key",
            "using nostalgic arcade-like chord progressions",
            "in a cozy, bit-crushed retro key center"
        ]
        return (
            f"A cozy and highly nostalgic 8-bit chiptune {mood} lofi track at a {tempo}, "
            f"{random.choice(harmonies)}. Featuring {random.choice(instruments)}, "
            f"accompanied by {random.choice(beats)}, and seasoned with {random.choice(textures)}. "
            f"Purely instrumental, no vocals. Inspired by the retro game theme: '{title}'."
        )

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
        prompt = get_prompt_for_mood(mood, title)

        if prompt_attempt == 0:
            print(f"[Generator] Generating track {next_seq} ('{title}' - [{mood}]) with Lyria 3 Pro...")
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
                    model="lyria-3-pro-preview",
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

# 16-Bit Visual Vocabulary Banks for Dynamic Prompt Generation
VISUAL_ELEMENTS = {
    "day": {
        "desk_objects": [
            "a glowing vintage CRT monitor showing green code lines",
            "a retro mechanical keyboard with custom keycaps",
            "a cozy cassette player next to a steaming mug",
            "an open notebook with a pixelated pen",
            "a nostalgic floppy disk on a wooden coaster"
        ],
        "window_views": [
            "soft warm morning sun shining over distant pixelated hills",
            "a quiet city skyline with pastel clouds and soft sunbeams",
            "a lush green pixel garden through the clean glass",
            "distant wind turbines on a nostalgic countryside hill"
        ],
        "ambience": [
            "a cute pixelated cat sleeping curled up on a soft pillow",
            "a small potted monstera plant casting gentle pixel shadows",
            "cozy warm fairy lights hanging softly near the curtain",
            "a retro desk lamp giving a soft golden glow"
        ],
        "palettes": [
            "soft pastel color scheme, highly aesthetic",
            "warm earth tones, cozy nostalgic 16-bit color grading",
            "gorgeous retro-chic aesthetic, clean pixel coloring"
        ]
    },
    "evening": {
        "window_views": [
            "warm orange twilight sunset over a pixelated street alley",
            "rain drops tapping softly on the glass with city neon reflections",
            "cozy brick alleyway under a golden evening glow",
            "passing classic retro streetcars under a purple twilight sky"
        ],
        "table_objects": [
            "a steaming porcelain mug of hot cocoa on the counter",
            "a vintage record player spinning a black vinyl disc",
            "a small vintage transistor radio with a warm glowing dial",
            "a cozy glass jar of cookies on a wooden table"
        ],
        "ambience": [
            "hanging ivy vines framing the wooden window",
            "a small potted succulent on the window sill",
            "shelves filled with pixelated retro books in the background",
            "a cozy warm glowing fireplace reflecting in the room"
        ]
    },
    "night": {
        "sky_views": [
            "starry night sky with a glowing purple crescent moon",
            "twinkling constellations over a dark pixelated landscape",
            "soft shooting stars falling in a deep midnight sky"
        ],
        "light_sources": [
            "a retro computer monitor glowing softly with a galaxy screensaver",
            "a cozy lava lamp glowing with a warm violet hue on the desk",
            "warm fairy lights draped beautifully over the bedframe",
            "soft neon blue and purple city lights bleeding through the window blinds"
        ],
        "ambience": [
            "a cute cat curled up sleeping peacefully near the keyboard",
            "soft blue and violet room shadows, vaporwave lighting",
            "cozy dark bedroom aesthetic, highly relaxing atmosphere"
        ]
    },
    "pixel": {
        "consoles": [
            "a cute retro handheld game console with buttons",
            "a vintage 80s arcade cabinet with a colorful joystick",
            "a nostalgic tabletop CRT TV with retro controllers next to it"
        ],
        "screen_content": [
            "a glowing green screen showing a classic 8-bit alien-shooter game",
            "a pixelated cosmic screen with tiny flying starships",
            "a classic retro 2D platformer game with pixelated blocks and coins"
        ],
        "backgrounds": [
            "a cosmic nebula with sparkling pixel stars and galaxies",
            "a retro gaming bedroom with grid synthwave posters",
            "a classic retro laser grid background, 80s nostalgic aesthetic"
        ]
    }
}

def generate_dynamic_image_prompt(mood):
    """
    Dynamically assembles a unique 16-bit visual prompt
    based on random combinations of objects and atmospheres.
    """
    if mood not in VISUAL_ELEMENTS:
        mood = "day"
        
    elem = VISUAL_ELEMENTS[mood]
    
    if mood == "day":
        obj = random.choice(elem["desk_objects"])
        view = random.choice(elem["window_views"])
        amb = random.choice(elem["ambience"])
        palette = random.choice(elem["palettes"])
        return f"detailed 16-bit lofi hip hop style pixel art of a cozy room workspace, outside {view}, on the desk {obj}, in the room {amb}, {palette}, 16:9 widescreen format"
        
    elif mood == "evening":
        obj = random.choice(elem["table_objects"])
        view = random.choice(elem["window_views"])
        amb = random.choice(elem["ambience"])
        return f"detailed 16-bit lofi jazzhop style pixel art of a cozy coffee shop window, outside {view}, on the table {obj}, {amb}, warm cozy lighting, 16:9 widescreen format"
        
    elif mood == "night":
        sky = random.choice(elem["sky_views"])
        light = random.choice(elem["light_sources"])
        amb = random.choice(elem["ambience"])
        return f"detailed 16-bit lofi sleep style pixel art of a cozy dark bedroom window looking out at {sky}, {light}, {amb}, relaxing cozy dark aesthetic, 16:9 widescreen format"
        
    elif mood == "pixel":
        console = random.choice(elem["consoles"])
        screen = random.choice(elem["screen_content"])
        bg = random.choice(elem["backgrounds"])
        return f"detailed 16-bit chiptune retro arcade style pixel art of {console}, the screen displays {screen}, set against {bg}, classic 8-bit gaming aesthetic, 16:9 widescreen format"

    return "detailed 16-bit lofi style pixel art, 16:9 widescreen format"

def generate_mood_image(mood, ai_client):
    """
    Generates a beautiful lofi pixel art image using gemini-3.1-flash-image
    corresponding to the specified mood globally. The image is generated natively
    and then programmatically converted to WebP in memory to guarantee lightweight transmission.
    """
    prompt = generate_dynamic_image_prompt(mood)
    print(f"[Generator] Generating daily pixel art image for mood '{mood}' using gemini-3.1-flash-image...")
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-3.1-flash-image",
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
