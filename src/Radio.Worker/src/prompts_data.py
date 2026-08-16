# Prompts Dataset for LofiRadio AI Music and Artwork Generation

# 1. Expanded vocabulary databases for randomized track title generation
# 40 adjectives and 40 nouns per mood (40 * 40 = 1600 base combinations per mood)
TITLE_WORDS = {
    "day": {
        "adj": [
            "Sunny", "Pixel", "Focus", "Cozy", "Desk", "Morning", "Warm", "Coffee", "Fresh", "Bright",
            "Gentle", "Silent", "Calm", "Golden", "Smooth", "Light", "Pure", "Lucid", "Velvet", "Radiant",
            "Serene", "Mellow", "Tranquil", "Peaceful", "Soothing", "Warm", "Soft", "Shining", "Clear", "Vibrant",
            "Lofi", "Aesthetic", "Minimal", "Simple", "Lazy", "Cozy", "Dreamy", "Restful", "Relaxed", "Hazy"
        ],
        "noun": [
            "Terminal", "Keys", "Chords", "Workspace", "Keyboard", "Window", "Code", "Beat", "Vibes", "Mug",
            "Screen", "Forest", "Leaves", "Raindrop", "Study", "Notebook", "Garden", "Sketch", "Breeze", "Pencil",
            "Desk", "Plants", "Mug", "Room", "Hills", "Coffee", "Latte", "Sunbeam", "Blinds", "Slippers",
            "Pen", "Canvas", "Aura", "Zen", "Chill", "Cafe", "Loft", "Studio", "Balcony", "Haven"
        ]
    },
    "evening": {
        "adj": [
            "Sunset", "Golden", "Mellow", "Twilight", "Orange", "Cozy", "Rainy", "Chill", "Velvet", "Dreamy",
            "Warm", "Soulful", "Vintage", "Amber", "Smooth", "Slow", "Peaceful", "Autumn", "Soft", "Dusty",
            "Smoky", "Calm", "Relaxed", "Serene", "Dim", "Glow", "Dusk", "Late", "Breezy", "Cozy",
            "Whispering", "Soothing", "Quiet", "Restful", "Tranquil", "Warm", "Rustling", "Shadowy", "Aesthetic", "Cozy"
        ],
        "noun": [
            "Station", "Dream", "Saxo", "Beat", "Train", "Avenue", "Lounge", "Steam", "Shadows", "Vibes",
            "Fireplace", "Cup", "Streetcar", "Boulevard", "Coffee", "Bookstore", "Rain", "Alley", "Lantern", "Tea",
            "Vinyl", "Jazz", "Saxophone", "Guitar", "Piano", "Trumpet", "Lamps", "Cafe", "Balcony", "Benches",
            "Raindrop", "Canopy", "Sidewalk", "Storefront", "Dusk", "Breeze", "Sip", "Starlight", "Porch", "Rug"
        ]
    },
    "night": {
        "adj": [
            "Midnight", "Neon", "Cosmic", "Deep", "Dreamy", "Silent", "Purple", "Starry", "Rainy", "Velvet",
            "Astral", "Calm", "Ethereal", "Lunar", "Floating", "Gentle", "Cozy", "Soothing", "Misty", "Shadow",
            "Nocturnal", "Serene", "Dark", "Sleeping", "Spaced", "Quiet", "Still", "Whispering", "Reverbed", "Dusty",
            "Nebula", "Starlit", "Crescent", "Peaceful", "Restful", "Chilled", "Hazy", "Blanketed", "Deep", "Dreamy"
        ],
        "noun": [
            "Hum", "Memory", "Rain", "Waves", "Lullaby", "Star", "Computer", "Sleeper", "Echo", "Glow",
            "Moon", "Beach", "Thunder", "Pillow", "Nebula", "Breeze", "Horizon", "Clock", "Blanket", "Tide",
            "Bed", "Room", "Nightsky", "Window", "Blinds", "Lava", "Fairy", "Lamp", "Crickets", "Ocean",
            "Soles", "Clouds", "Pajamas", "Sleep", "Slumber", "Whisper", "Stardust", "Constellation", "Slippers", "Silence"
        ]
    },
    "pixel": {
        "adj": [
            "8-Bit", "Chiptune", "Retro", "Pixel", "Arcade", "Glitch", "Console", "Level", "Vintage", "Handheld",
            "Sprite", "Classic", "Polygon", "Vector", "Binary", "Playful", "Cozy", "Tiny", "Soundcard", "Gamepad",
            "Pixelated", "Blocky", "Amiga", "Sega", "NES", "Gameboy", "Nostalgic", "Cute", "Digital", "Dithered",
            "Vibrant", "Charming", "Sprites", "Soundchip", "Arcade", "Retro", "Tiny", "Blocky", "Lofi", "Pixel"
        ],
        "noun": [
            "Castle", "Dungeon", "Quest", "Hero", "Sprites", "Savepoint", "Cartridge", "Screen", "Forest", "Heart",
            "Joypad", "Joystick", "Coins", "Soundchip", "Invader", "Grid", "Pixelart", "Trophy", "Boss", "Overworld",
            "Console", "Cabinet", "Tabletop", "Blip", "Bleep", "Soundcard", "Controller", "Buttons", "Map", "Key",
            "Level", "Player", "Npc", "Dungeon", "Village", "Tavern", "Sword", "Shield", "Item", "Inventory"
        ]
    },
    "synthwave": {
        "adj": [
            "Neon", "Retro", "Outrun", "Cyber", "Synth", "Sunset", "Laser", "Digital", "Grid", "Turbo",
            "Chrome", "Vector", "Infinite", "Speed", "Cosmic", "Cruiser", "Future", "Virtual", "Stellar", "Horizon",
            "Sunset", "Cyberpunk", "Retrowave", "Outrun", "Velocity", "Dynamic", "Aesthetic", "Glow", "Hot", "Pink",
            "Neonblue", "Magenta", "Drive", "Sleek", "Cruising", "Fast", "Hyper", "Vapor", "Vaporwave", "Synth"
        ],
        "noun": [
            "Driver", "Horizon", "Palms", "Highway", "Racer", "Cruiser", "Skyline", "Dreams", "Future", "Overdrive",
            "Sunset", "Neonlight", "Grid", "Highway", "Dashboard", "Sportsbar", "Laser", "Outrun", "Cassette", "Neon",
            "Car", "Coupe", "Spoiler", "Underglow", "Tail", "Lights", "Cityline", "Vapor", "Vibe", "Rhythm",
            "Velocity", "Engine", "Cockpit", "Radio", "Track", "Suns", "Vector", "Palms", "Avenue", "Overdrive"
        ]
    }
}

# Thematic, brand-free location/time suffix modifiers (20 suffixes per mood!)
# 1600 base combinations * 21 possibilities (no-suffix + 20 suffixes) = 33,600+ unique titles per mood, 168,000+ total!
TITLE_SUFFIXES = {
    "day": [
        "in Tokyo", "at the Desk", "by the Window", "in the Library", "under the Sun", 
        "at the Cafe", "in the Loft", "near the Garden", "in the Classroom", "by the River", 
        "on a Rainy Day", "during Class", "at Sunrise", "with Warm Coffee", "in Kyoto", 
        "on the Balcony", "during Spring", "in the Attic", "near the Park", "on Sunday"
    ],
    "evening": [
        "at Dusk", "in the Lounge", "by the Fireplace", "in Paris", "at the Bar", 
        "near the Subway", "on the Avenue", "at Sunset", "in New York", "with Soft Jazz", 
        "in the Alley", "under the Lantern", "at the Counter", "on the Rooftop", "by the River", 
        "in Autumn", "with Warm Tea", "during Evening Rain", "on Friday", "in the Bookstore"
    ],
    "night": [
        "at Midnight", "under the Moon", "in the Dark", "by the Sea", "in the Bedroom", 
        "under the Stars", "in the Slumber", "at Night", "near the Ocean", "in the Nebula", 
        "in London", "during Thunder", "on the Beach", "in Dreams", "under the Blanket", 
        "at 3 AM", "in the Clouds", "with Cozy Rain", "in the Void", "near the Lighthouse"
    ],
    "pixel": [
        "in Level 1", "at the Arcade", "in the Dungeon", "on the Screen", "in the Overworld", 
        "at the Savepoint", "on the Gameboy", "in the Castle", "on the NES", "in the Forest", 
        "during Play", "at Boss Fight", "in the Tavern", "on Amiga", "on Retro-PC", 
        "in the Matrix", "on Cartridge", "in 8-Bit", "in Level 2", "on Gamepad"
    ],
    "synthwave": [
        "on the Grid", "at the Horizon", "on the Highway", "in the Outrun", "under Neon", 
        "on the Dashboard", "in the Future", "at the Sportsbar", "on Turbo", "in Miami", 
        "at Sunset", "in the Cyber-City", "on Chrome", "at Midnight", "on the Runway", 
        "in 1988", "by the Palms", "on the Skyline", "in the Void", "on Overdrive"
    ]
}

# 2. Audio prompt synthesis parameters for Google Vertex AI Lyria 3 Pro
AUDIO_TEMPOS = [
    "slow-paced 70 BPM", "relaxed 73 BPM", "laid-back 76 BPM", "mellow 79 BPM", 
    "cozy 82 BPM", "chill 85 BPM", "grooving 88 BPM"
]

# Randomized audio genre descriptions and themes (all Lofi are strictly relaxing, warm, and cozy!)
AUDIO_GENRES = {
    "day": [
        {"genre": "relaxing, peaceful, and highly focused day lofi hip hop track", "theme": "cozy theme"},
        {"genre": "calming, warm, and soothing focused daytime lofi beat", "theme": "peaceful study theme"},
        {"genre": "gentle, serene, and deeply relaxing focused day lofi track", "theme": "calm workspace theme"},
        {"genre": "cozy, peaceful, and mellow focused afternoon lofi hip hop vibe", "theme": "focused studying theme"}
    ],
    "evening": [
        {"genre": "warm, relaxing, and soulful evening jazzhop lofi track", "theme": "cozy theme"},
        {"genre": "soothing, mellow, and deeply relaxing evening jazzhop lofi beat", "theme": "chill coffee shop theme"},
        {"genre": "gentle, cozy, and relaxing twilight jazzhop lofi track", "theme": "relaxed evening theme"},
        {"genre": "peaceful, warm, and calming evening lounge jazzhop lofi soundscape", "theme": "soulful sunset theme"}
    ],
    "night": [
        {"genre": "ultra-mellow, dreamy, and peaceful night sleep lofi track", "theme": "cozy theme"},
        {"genre": "deeply relaxing, calm, and soothing bedtime sleep lofi track", "theme": "dreamy night theme"},
        {"genre": "gentle, quiet, and serene midnight sleep lofi soundscape", "theme": "peaceful slumber theme"},
        {"genre": "soothing, warm, and highly relaxing late-night sleep lofi beat", "theme": "calm sleeping theme"}
    ],
    "pixel": [
        {"genre": "cozy, relaxing, and highly nostalgic 8-bit chiptune pixel lofi track", "theme": "retro game theme"},
        {"genre": "gentle, calming, and nostalgic 16-bit soundchip retro lofi beat", "theme": "vintage pixelated game theme"},
        {"genre": "peaceful, relaxing, and playful 8-bit pulse-wave pixel lofi track", "theme": "retro console theme"},
        {"genre": "soothing, nostalgic, and deeply relaxing chiptune-inspired pixel lofi vibe", "theme": "cozy arcade theme"}
    ],
    "synthwave": [
        {"genre": "driving, nostalgic, and retro-futuristic synthwave retrowave track", "theme": "cyber theme"},
        {"genre": "soaring, nostalgic, and cinematic outrun synthwave track", "theme": "retro-futuristic cyber theme"},
        {"genre": "upbeat, melodic, and 1980s inspired retrowave synthwave track", "theme": "neon outrun theme"},
        {"genre": "driving, epic, and highly nostalgic retro-electronic synthwave track", "theme": "cyberpunk dreams theme"}
    ]
}

AUDIO_ELEMENTS = {
    "day": {
        "instruments": [
            "warm electric piano and soft fingerstyle acoustic guitar",
            "mellow vintage electric keys and clean retro electric guitar riffs",
            "organic acoustic kalimba arpeggios, warm vintage electric keys, and a clean electric bass",
            "cozy vintage reed organ chords, clean electric guitar, and soft synthesized bells",
            "warm retro organ chords, soothing acoustic slide guitar, and a subtle electric piano",
            "smooth electric piano, light steel-string acoustic guitar, and soft vibraphone notes",
            "vintage acoustic piano keys, smooth nylon string guitar chords, and soft synthesized bells",
            "warm vintage tine electric piano chords, gentle acoustic guitar pluckings, and a soft bassline",
            "soothing acoustic harp arpeggios, clean electric guitar harmonies, and vintage keys",
            "soft vintage upright piano melodies, clean fingerstyle acoustic guitar, and warm pads"
        ],
        "beats": [
            "dusty lofi boom-bap drums with a gentle kick and soft snare",
            "relaxed lofi hip hop swing beats with a warm crackling rimshot",
            "laid-back organic acoustic percussion and a very soft kick-snare pattern",
            "chill down-tempo lofi drum loop with heavily filtered hi-hats",
            "soft shuffle drums and a warm, steady bassline",
            "mellow dusty low-pass filtered kick and a crisp woodblock snare hit",
            "gentle 12-bit sampler lofi boom-bap rhythm with laid-back swing",
            "soft low-fidelity acoustic drum kit beats with filtered shaker hats"
        ],
        "textures": [
            "soft vinyl crackle and distant morning birds singing",
            "cozy coffee shop background room-tone with faint chatter and cup clinks",
            "gentle morning breeze rustling through open windows",
            "subtle analog tape hiss and the warm sound of distant morning rain",
            "soft wind chimes and warm analog record dust noise",
            "faint analog clock ticking and soft outdoor wind rustle",
            "cozy fireplace crackle and gentle keyboard typing sounds",
            "warm vintage record dust crackle and soft window-tapping rain"
        ],
        "harmonies": [
            "in a warm major-seventh progression",
            "using cozy major chord structures",
            "in a peaceful, soothing major key center",
            "in an optimistic major-ninth harmony",
            "using smooth, heartwarming major cadences",
            "with gentle, uplifting major chord voicings"
        ]
    },
    "evening": {
        "instruments": [
            "jazzy electric guitar chords and a smooth soulful saxophone lead",
            "warm hollow-body jazz guitar and a mellow muted trumpet melody",
            "relaxed jazz-hop piano chords and a soft, warm acoustic double bass",
            "cozy jazz piano, a warm breathy tenor saxophone, and a light vibraphone",
            "mellow retro electric keys, a clean jazz hollow-body guitar, and a soft flute lead",
            "warm retro drawbar organ chords, smooth jazzy guitar riffs, and a mellow contrabass",
            "smoky vintage grand piano keys, mellow hollow-body jazz guitar, and a warm saxophone",
            "relaxed jazz-hop electric keys, clean jazz-guitar pluckings, and a soft upright bass",
            "warm electric drawbar organ swells, smooth muted trumpet melodies, and a mellow jazz guitar",
            "soft vintage upright piano chords, a warm breathing flute lead, and a light contrabass"
        ],
        "beats": [
            "slow-paced jazzy lofi snare and brush drums",
            "relaxed dusty hip hop drum swing with a warm rimshot",
            "mellow organic rimshots, laid-back snare beats, and a swinging ride cymbal",
            "chill jazzy boom-bap rhythm with heavily filtered, soft percussion",
            "smooth swing snare and brush drums with a warm, driving jazz beat",
            "dusty swing-hop snare, soft acoustic kicks, and a mellow ride cymbal",
            "mellow low-passed jazz-hop drum kit loops with organic woodblock hits",
            "soft 12-bit filtered jazz brush drums and an organic rimshot rhythm"
        ],
        "textures": [
            "a soft crackling fireplace in the background",
            "gentle evening rain tapping on a glass window",
            "warm, dusty vinyl record noise and faint street ambiance",
            "cozy evening cafe room-tone and a distant city hum",
            "analog tape saturation and soft wind rustling in the twilight",
            "distant street jazz musicians, warm vinyl dust, and faint traffic hum",
            "soft coffee shop espresso steam and gentle evening rain soundscapes",
            "warm analog tape warble and cozy twilight room ambiance"
        ],
        "harmonies": [
            "in a jazzy minor-ninth chord progression",
            "using smooth, elegant jazz minor chords",
            "with sophisticated major-ninth and minor-ninth harmonies",
            "in a warm Dorian mode minor-seventh chord progression",
            "using cozy, elegant minor-eleventh jazz voicings",
            "with rich, slow-moving jazz minor cadences"
        ]
    },
    "night": {
        "instruments": [
            "soft reverbed piano and slow ambient synthesizer pads",
            "ultra-mellow vintage electric keys and a warm, breathing sub-bass",
            "dreamy celesta bells and gentle sweeping ambient textures",
            "soft, distant electric piano chords and slow-evolving spacey pads",
            "mellow glockenspiel notes, a very soft acoustic nylon guitar, and deep synth pads",
            "slow-moving reverbed vintage electric keys, soft ambient wave-like synths, and a deep bass hum",
            "dreamy reverbed upright piano keys, warm sleeping ambient pads, and slow synth swells",
            "soft nylon-string acoustic guitar arpeggios, distant celestial keys, and slow-moving deep sub pads",
            "mellow glass-like synthesized bells, slow-evolving warm pads, and a deep, breathing synth bass",
            "slow-paced reverbed electric keys, gentle ambient soundscape swells, and an organic deep bassline"
        ],
        "beats": [
            "extremely slow-paced lofi brush beats",
            "minimalist dusty kick and soft rimshot",
            "a very gentle, laid-back low-pass filtered drum track",
            "soft, slow-tempo organic heartbeat-like percussion",
            "no heavy drums, just an ultra-slow, breathing ambient synth pulse",
            "slow low-passed organic kick and soft brush snare tapping",
            "dusty, slow-tempo rimshot beat with low-pass filtered shaker hats",
            "very soft down-tempo organic sampler drums with faint, warm cymbals"
        ],
        "textures": [
            "a gentle, steady rain falling on a quiet neon-lit city street",
            "soft, rhythmic waves lapping on a quiet night beach",
            "warm analog tape hiss and a cozy room ambiance",
            "gentle midnight crickets and a soft, warm summer breeze",
            "distant thunder claps and steady, soothing rain soundscapes",
            "faint bedroom wind chime, warm tape hiss, and slow wind sweeps",
            "soft nocturnal crickets, warm analog record dust, and soothing sea waves",
            "gentle ocean wave swells and a warm cassette tape warble"
        ],
        "harmonies": [
            "in a slow-moving, heavily reverbed minor-seventh progression",
            "using deep, ambient minor chord structures",
            "in an ultra-soft, slow-evolving atmospheric progression",
            "in a dreamy minor-ninth and minor-eleventh key signature",
            "using deep, spacey minor-seventh atmospheric cadences",
            "with slow, breathing, and soothing modal minor harmonies"
        ]
    },
    "pixel": {
        "instruments": [
            "vintage 8-bit square-wave leads and nostalgic retro game-console triangle-wave bass",
            "playful 16-bit FM-synthesis chords and retro handheld console square-wave melodies",
            "warm retro game-console synth arpeggios and nostalgic 8-bit pulse-wave chords",
            "pixelated sound chip square-wave melodies and a soft vintage synthesizer lead",
            "soft 8-bit pulse-wave chiptune leads, retro chord progressions, and a vintage game-synth pad",
            "nostalgic 16-bit soundcard piano chords, playful square-wave arpeggios, and low-passed retro bass",
            "vintage 8-bit pulse-wave melodies, playful square-wave arpeggiators, and a warm triangle-wave bass",
            "nostalgic 16-bit FM-synthesis electric keys, playful chiptune arpeggios, and a retro low-passed bass",
            "playful 8-bit square-wave chord progressions, retro game-sound leads, and triangle-wave bass",
            "nostalgic game-console synthesized keys, soft 16-bit soundcard chords, and low-passed chip bass"
        ],
        "beats": [
            "relaxing lofi hip hop drum beats with a dusty 12-bit crunch",
            "mellow dusty organic chip-drums and soft retro game-console noise",
            "laid-back organic chiptune-inspired snare swing with a retro kick",
            "chill down-tempo 12-bit sampler drums with soft, bit-crushed hi-hats",
            "retro 8-bit arcade-style drum machine rhythm, low-passed and relaxed",
            "mellow bit-crushed chip-drums, soft retro kicks, and a relaxed 8-bit rhythm",
            "chill down-tempo 16-bit drum sampler beats with filtered, pixelated percussion",
            "gentle dusty 8-bit soundchip drums with organic rimshots and soft, retro swing"
        ],
        "textures": [
            "playful retro game start bleeps and soft pixelated sound effects",
            "warm retro game-room room-tone and soft analog console noise",
            "cozy low-fidelity 8-bit sound-effects and gentle static",
            "faint sounds of an old CRT television humming and retro arcade ambiance",
            "vintage 8-bit game pause sounds and warm cassette tape warble",
            "playful 8-bit power-up sounds, warm retro game-room hum, and soft static",
            "faint vintage CRT monitor humming and soft, nostalgic pixelated wind sweeps",
            "retro arcade room background hum and cozy game-console soundcard static"
        ],
        "harmonies": [
            "in a playful, retro minor key",
            "using nostalgic arcade-like chord progressions",
            "in a cozy, bit-crushed retro key center",
            "using playful, retro 16-bit minor-seventh chord structures",
            "in a warm, blocky game-console minor progression",
            "with nostalgic, bit-crushed chiptune minor-seventh cadences"
        ]
    },
    "synthwave": {
        "instruments": [
            "nostalgic 1980s analog synthesizer leads, warm retro-futuristic pads, and a rolling arpeggiated synth bassline",
            "vintage retrowave key chords, soaring synthesizer solos, and a driving synthwave running bassline",
            "dreamy outrun synthesizer pads, retro FM-synthesis leads, and a pumping electronic bassline",
            "warm analog polyphonic synth chords, melodic retro lead synthesizers, and an upbeat synthwave bassline",
            "cinematic outrun synthesizer swells, melodic retro key arpeggios, and a steady retro-futuristic synth bassline",
            "vintage 1980s analog synthesizer pluckings, warm outrun pads, and a rolling arpeggiated electronic bass",
            "melodic retro lead synthesizers, warm polyphonic analog synth chords, and a pumping retrowave bassline",
            "cinematic outrun synthesizer sweeps, nostalgic polyphonic key progressions, and a steady running bass",
            "warm analog 80s synthesizer chords, retro-futuristic leads, and a rolling arpeggiated electronic bassline",
            "nostalgic polyphonic synth arpeggios, warm outrun synthesizer swells, and a pumping retrowave bass"
        ],
        "beats": [
            "powerful retro drum machines with classic gated reverb snares and steady, driving 4-on-the-floor kicks",
            "nostalgic 80s electronic down-tempo beats with thick gated reverb snares and steady hi-hats",
            "chill synthwave drum patterns featuring heavy gated snares and an upbeat driving kick pattern",
            "retro drum machine patterns with loud, distinct gated snare hits and a driving electronic kick beat",
            "driving retro drum machines featuring powerful gated reverb snare hits and a steady electronic kick rhythm",
            "nostalgic 80s drum loops with loud gated snares, tight hi-hats, and a driving electronic kick",
            "chill down-tempo synthwave drum kit beats with distinctive, loud gated reverb snares",
            "retro electronic drum machines with powerful gated snares and an upbeat driving kick beat"
        ],
        "textures": [
            "faint CRT monitor hum and distant retro-arcade synthesizer sweeps",
            "retro-futuristic analog synthesizer sweeps and warm vintage tape saturation noise",
            "chill outrun wind sweeps and soft neon underglow hum noise",
            "vintage cassette tape warble and retro synth riser sweeps",
            "cozy analog console hum and distant digital wind chime sweeps",
            "faint 1980s CRT monitor humming and retro-futuristic analog synthesizer riser sweeps",
            "warm analog tape saturation noise and cozy outrun wind sweep soundscapes",
            "chill neon underglow hum static and soft vintage synthesizer sweeps"
        ],
        "harmonies": [
            "in a moody, nostalgic 80s minor chord progression",
            "using epic retrowave minor-seventh harmonies",
            "in a warm, cinematic retro-futuristic key center",
            "in an epic, dark-synth minor-ninth chord progression",
            "using cinematic retrowave minor-seventh and major-seventh cadences",
            "with moody, slow-moving retro-futuristic minor harmonies"
        ]
    }
}

# 3. 16-Bit pixel art visual elements for Gemini 3.1 Image Generation
VISUAL_ELEMENTS = {
    "day": {
        "desk_objects": [
            "a glowing vintage CRT monitor showing green code lines",
            "a retro mechanical keyboard with custom keycaps",
            "a cozy cassette player next to a steaming mug",
            "an open notebook with a pixelated pen",
            "a nostalgic floppy disk on a wooden coaster",
            "a retro pixelated desk calendar and vintage pencil holder",
            "a miniature retro pixel globe on a wooden shelf"
        ],
        "window_views": [
            "soft warm morning sun shining over distant pixelated hills",
            "a quiet city skyline with pastel clouds and soft sunbeams",
            "a lush green pixel garden through the clean glass",
            "distant wind turbines on a nostalgic countryside hill",
            "gorgeous soft mountain silhouettes under a clear morning sky",
            "a peaceful suburban street with tiny pixel cars passing"
        ],
        "ambience": [
            "a cute pixelated cat sleeping curled up on a soft pillow",
            "a small potted monstera plant casting gentle pixel shadows",
            "cozy warm fairy lights hanging softly near the curtain",
            "a retro desk lamp giving a soft golden glow",
            "shelves with tiny pixelated houseplants and retro cassettes",
            "a soft vintage curtain blowing gently in a morning breeze"
        ],
        "palettes": [
            "soft pastel color scheme, highly aesthetic",
            "warm earth tones, cozy nostalgic 16-bit color grading",
            "gorgeous retro-chic aesthetic, clean pixel coloring",
            "aesthetic light sepia tones, warm nostalgic morning lighting",
            "vibrant warm yellow and soft mint green 16-bit pixel shading"
        ]
    },
    "evening": {
        "window_views": [
            "warm orange twilight sunset over a pixelated street alley",
            "rain drops tapping softly on the glass with city neon reflections",
            "cozy brick alleyway under a golden evening glow",
            "passing classic retro streetcars under a purple twilight sky",
            "distant suspension bridge outlines under a brilliant orange sunset",
            "a cozy rainy cafe street under beautiful glowing street lamps"
        ],
        "table_objects": [
            "a steaming porcelain mug of hot cocoa on the counter",
            "a vintage record player spinning a black vinyl disc",
            "a small vintage transistor radio with a warm glowing dial",
            "a cozy glass jar of cookies on a wooden table",
            "a retro typewriter with a sheet of paper on the table",
            "a cozy porcelain tea set on a beautiful retro tablecloth"
        ],
        "ambience": [
            "hanging ivy vines framing the wooden window",
            "a small potted succulent on the window sill",
            "shelves filled with pixelated retro books in the background",
            "a cozy warm glowing fireplace reflecting in the room",
            "glowing neon signs from nearby shops reflecting on the table",
            "a retro wooden coat rack with a hanging scarf"
        ]
    },
    "night": {
        "sky_views": [
            "starry night sky with a glowing purple crescent moon",
            "twinkling constellations over a dark pixelated landscape",
            "soft shooting stars falling in a deep midnight sky",
            "a full glowing lunar moon with passing pixelated dark clouds",
            "a gorgeous cosmic aurora borealis in a deep night sky"
        ],
        "light_sources": [
            "a retro computer monitor glowing softly with a galaxy screensaver",
            "a cozy lava lamp glowing with a warm violet hue on the desk",
            "warm fairy lights draped beautifully over the bedframe",
            "soft neon blue and purple city lights bleeding through the window blinds",
            "a glowing plasma ball giving an aesthetic violet hum",
            "a small retro bedside lamp with a warm, soft peach lampshade"
        ],
        "ambience": [
            "a cute cat curled up sleeping peacefully near the keyboard",
            "soft blue and violet room shadows, vaporwave lighting",
            "cozy dark bedroom aesthetic, highly relaxing atmosphere",
            "a cozy warm blanket draped softly on a rocking chair",
            "glowing digital clock numbers showing midnight in the dark"
        ]
    },
    "pixel": {
        "consoles": [
            "a cute retro handheld game console with buttons",
            "a vintage 80s arcade cabinet with a colorful joystick",
            "a nostalgic tabletop CRT TV with retro controllers next to it",
            "a classic 16-bit home console connected to a small television",
            "a retro arcade zone booth with multiple glowing cabinet screens"
        ],
        "screen_content": [
            "a glowing green screen showing a classic 8-bit alien-shooter game",
            "a pixelated cosmic screen with tiny flying starships",
            "a classic retro 2D platformer game with pixelated blocks and coins",
            "a retro 16-bit RPG game screen with text dialog and tiny characters",
            "a pixelated racing game showing a cute red car on a grid highway"
        ],
        "backgrounds": [
            "a cosmic nebula with sparkling pixel stars and galaxies",
            "a retro gaming bedroom with grid synthwave posters",
            "a classic retro laser grid background, 80s nostalgic aesthetic",
            "a futuristic cyber-city background with glowing pixelated towers",
            "a starry retro arcade room with floating neon polygon details"
        ]
    },
    "synthwave": {
        "vehicles": [
            "a classic 1980s futuristic sports car driving silhouette",
            "a retro neon sports car cruising steadily",
            "a sleek wireframe sports cruiser silhouette",
            "a futuristic cyber sports car driving towards the horizon",
            "a classic 80s luxury coupe silhouette driving on a grid road"
        ],
        "suns": [
            "a massive glowing pink and orange neon grid sun",
            "a giant retro vector sun setting on the horizon",
            "a bright glowing synthwave sun with horizontal slice bars",
            "a giant half-grid sun with orange and magenta neon horizontal lines",
            "a retro vector sun casting a vibrant purple and orange glow"
        ],
        "backgrounds": [
            "a beautiful infinite pink and purple wireframe laser grid",
            "a retro-futuristic purple twilight skyline with tall neon towers",
            "a cosmic outrun highway lined with glowing neon palm trees",
            "an infinite outrun landscape with retro-futuristic grid grids",
            "a starry retrowave galaxy lined with wireframe mountains and grids"
        ]
    }
}

# 4. Randomized Visual prompt templates for Gemini 3.1 Image Generation (4 distinct perspectives/styles per mood!)
VISUAL_TEMPLATES = {
    "day": [
        "detailed 16-bit lofi hip hop style pixel art of a cozy room workspace, outside {view}, on the desk {obj}, in the room {amb}, {palette}, 16:9 widescreen format",
        "aesthetic 16-bit lofi pixel art illustration of a quiet sunny study room, on the desk we see {obj}. Outside the window is {view}, while inside the room {amb}. {palette}, 16:9 widescreen format",
        "charming 16-bit retro lofi room interior pixel art: {amb}. On the wooden desk sits {obj}, looking out of the cozy window to see {view}. {palette}, 16:9 widescreen format",
        "relaxing lofi workspace scene in beautiful 16-bit pixel art style, {palette}. A warm room featuring {amb}, with {obj} on the desk. The window view shows {view}, 16:9 widescreen format"
    ],
    "evening": [
        "detailed 16-bit lofi jazzhop style pixel art of a cozy coffee shop window, outside {view}, on the table {obj}, {amb}, warm cozy lighting, 16:9 widescreen format",
        "aesthetic 16-bit jazzhop cafe window seat in warm pixel art. Outside is {view}, while on the table sits {obj}. In the background, there are {amb}. Warm cozy lighting, 16:9 widescreen format",
        "charming retro 16-bit cafe interior pixel art scene. Cozy coffee shop vibes with {amb}. On the wooden counter is {obj}, looking out the window at {view}. 16:9 widescreen format",
        "relaxing evening coffee shop pixel art illustration, warm amber glow. A table featuring {obj}, surrounded by {amb}, with a lovely glass window view of {view}, 16:9 widescreen format"
    ],
    "night": [
        "detailed 16-bit lofi sleep style pixel art of a cozy dark bedroom window looking out at {sky}, {light}, {amb}, relaxing cozy dark aesthetic, 16:9 widescreen format",
        "aesthetic 16-bit sleep-lofi midnight bedroom interior, dark cozy pixel art. Looking out of the wide window to see {sky}. The room is lit softly by {light}, creating {amb}, 16:9 widescreen format",
        "charming 16-bit dark retro bedroom pixel art, relaxing nocturnal vibes. Softly illuminated by {light}, showing {amb}. The window overlooks {sky}, 16:9 widescreen format",
        "relaxing night bedroom scene in beautiful 16-bit pixel art, cozy dark aesthetic. A bedroom featuring {amb}, lit by {light}. Through the window is a starry view of {sky}, 16:9 widescreen format"
    ],
    "pixel": [
        "detailed 16-bit chiptune retro arcade style pixel art of {console}, the screen displays {screen}, set against {bg}, classic 8-bit gaming aesthetic, 16:9 widescreen format",
        "aesthetic 16-bit retro game setup in pixel art style. Up close on {console} where {screen}. Set against a beautiful backdrop of {bg}, 80s nostalgic gaming vibes, 16:9 widescreen format",
        "charming 80s gamer room corner in 16-bit pixel art. Centered on {console} with {screen}, surrounded by {bg}, classic retro-arcade nostalgic style, 16:9 widescreen format",
        "nostalgic chiptune-inspired 16-bit pixel art scene. Featuring {console} displaying {screen}, set against {bg}, vibrant retro-gaming color palette, 16:9 widescreen format"
    ],
    "synthwave": [
        "detailed 16-bit retro-futuristic outrun synthwave style pixel art of {vehicle} driving towards {sun}, set against {bg}, vibrant purple and hot pink color palette, aesthetic 1980s retrowave vibes, 16:9 widescreen format",
        "aesthetic 1980s outrun style 16-bit pixel art illustration. Featuring {vehicle} cruising steadily towards {sun}, surrounded by {bg}. Vibrant hot pink, neon blue, and purple color scheme, 16:9 widescreen format",
        "charming retro-futuristic retrowave pixel art scene. An epic 16-bit view of {vehicle} driving on a highway towards {sun}, set against {bg}. Glowing neon wires, outrun aesthetics, 16:9 widescreen format",
        "cinematic synthwave highway in beautiful 16-bit pixel art, 80s retrowave vibes. {vehicle} driving into the sunset of {sun}, surrounded by the cosmic landscape of {bg}, 16:9 widescreen format"
    ]
}
