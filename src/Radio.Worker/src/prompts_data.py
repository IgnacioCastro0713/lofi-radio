# Dynamic Prompts Loader from JSON for LofiRadio AI Music and Artwork Generation
import json
import os

# Load the prompts JSON database
json_path = os.path.join(os.path.dirname(__file__), "prompts_data.json")
with open(json_path, "r", encoding="utf-8") as f:
    _data = json.load(f)

TITLE_WORDS = _data["TITLE_WORDS"]
TITLE_SUFFIXES = _data["TITLE_SUFFIXES"]
AUDIO_TEMPOS = _data["AUDIO_TEMPOS"]
AUDIO_GENRES = _data["AUDIO_GENRES"]
AUDIO_ELEMENTS = _data["AUDIO_ELEMENTS"]
VISUAL_ELEMENTS = _data["VISUAL_ELEMENTS"]
VISUAL_TEMPLATES = _data["VISUAL_TEMPLATES"]
AUDIO_TEMPLATES = _data["AUDIO_TEMPLATES"]
