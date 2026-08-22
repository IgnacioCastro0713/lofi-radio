window.lofiPlayer = {
    audio: null,
    dotNetRef: null,
    syncInterval: null,
    nextTrackData: null,   // Pre-loaded metadata for the upcoming track to support seamless locked screen transitions
    userVolume: 0.5,       // Tracks the user's selected volume
    fadeDuration: 5,       // Duration of the fade-out effect in seconds
    fadeInDuration: 3,     // Duration of the fade-in effect in seconds
    lastUpdateTime: 0,     // Timestamp for SignalR network throttling
    audioCtx: null,        // Web Audio API context for visualizer
    analyser: null,
    sourceNode: null,
    animFrameId: null,
    freqData: null,

    init: function (dotNetReference) {
        this.dotNetRef = dotNetReference;
        if (!this.audio) {
            // Bind to the hidden, native HTML5 audio element on the Blazor page
            this.audio = document.getElementById("nativeLofiAudio");
            
            if (this.audio) {
                // Set initial volume
                this.audio.volume = this.userVolume;

                // iOS 18+ Hack: Force the audio session category to 'playback'
                // This makes WebKit ignore the physical Mute/Silent switch on iPhones!
                if (navigator.audioSession) {
                    try {
                        navigator.audioSession.type = 'playback';
                        console.log("[lofiPlayer] iOS audioSession set to 'playback' (bypassing physical mute switch).");
                    } catch (e) {
                        console.warn("[lofiPlayer] Failed to set audioSession type:", e);
                    }
                }

                // Detect iOS/Apple devices to apply specific CSS and layout rules
                const isIOS = /iPad|iPhone|iPod/.test(navigator.platform) || 
                              (navigator.userAgent.includes("Mac") && "ontouchend" in document);
                if (isIOS) {
                    document.documentElement.classList.add('is-ios');
                    console.log("[lofiPlayer] iOS device detected. Native volume control constraint active.");
                }

                // Register native Media Session play/pause actions (lock screen support)
                if ('mediaSession' in navigator) {
                    navigator.mediaSession.setActionHandler('play', () => {
                        this.play();
                    });
                    navigator.mediaSession.setActionHandler('pause', () => {
                        this.pause();
                    });
                }
                
                // Add event listeners to notify Blazor of playback changes
                this.audio.addEventListener('play', () => {
                    this.dotNetRef.invokeMethodAsync('OnPlaybackStatusChanged', true);
                    this.startSyncTimer(); // Start smooth local UI updates
                });
                this.audio.addEventListener('pause', () => {
                    this.dotNetRef.invokeMethodAsync('OnPlaybackStatusChanged', false);
                    this.stopSyncTimer(); // Stop local UI updates to conserve resources
                });
                this.audio.addEventListener('timeupdate', () => {
                    const currentTime = this.audio.currentTime;
                    const duration = this.audio.duration;
                    
                    // SMOOTH TRANSITION ENGINE (Fade-In & Fade-Out)
                    if (duration) {
                        const timeRemaining = duration - currentTime;
                        
                        // 1. FADE-OUT: Gradual volume decrease during the last 5 seconds of the song
                        if (timeRemaining < this.fadeDuration) {
                            const ratio = Math.max(0, timeRemaining / this.fadeDuration);
                            this.audio.volume = this.userVolume * ratio;
                        }
                        // 2. FADE-IN: Gradual volume increase during the first 3 seconds of the new song
                        else if (currentTime < this.fadeInDuration) {
                            const ratio = Math.max(0, currentTime / this.fadeInDuration);
                            this.audio.volume = this.userVolume * ratio;
                        }
                        // 3. NORMAL PLAYBACK: Maintain user-configured volume
                        else if (this.audio.volume !== this.userVolume) {
                            this.audio.volume = this.userVolume;
                        }
                    }

                    // IMPROVEMENT 2: SignalR throttling - limit network synchronization to once every 5 seconds to minimize WebSocket traffic
                    const now = Date.now();
                    if (now - this.lastUpdateTime >= 5000) {
                        this.lastUpdateTime = now;
                        this.dotNetRef.invokeMethodAsync('OnTimeUpdate', currentTime, duration);
                    }
                });
                this.audio.addEventListener('ended', () => {
                    // Transition synchronously first to preserve the event context and satisfy strict mobile security!
                    if (this.nextTrackData) {
                        console.log(`[lofiPlayer] Synchronous seamless transition in 'ended' context to: '${this.nextTrackData.title}'`);
                        const next = this.nextTrackData;
                        this.nextTrackData = null; // Clear pre-load cache
                        this.syncAndPlay(next.audioUrl, 0, next.title, next.mood, next.artworkUrl);
                    } else {
                        this.stopSyncTimer();
                    }

                    // Notify Blazor Server in the background afterwards
                    this.dotNetRef.invokeMethodAsync('OnTrackEnded');
                });
                this.audio.addEventListener('error', (e) => {
                    console.warn("Audio playback error (possibly due to a daily GCS playlist wipe). Attempting self-healing re-sync with server...", e);
                    // Call OnTrackEnded to force Blazor to fetch the fresh, newly updated track from Firestore and resume the stream!
                    this.dotNetRef.invokeMethodAsync('OnTrackEnded');
                });

                // IMPROVEMENT 1: Global click event delegation.
                // Register the event listener once on the document so it remains unaffected when Blazor recreates the button.
                document.addEventListener('click', (e) => {
                    const playBtn = e.target.closest('.bottom-play-btn');
                    if (playBtn) {
                        this.unlock();
                    }
                });

                // Global Keyboard Shortcuts (Space: Play/Pause, M: Mute, F: Fullscreen, Arrows: Volume)
                window.addEventListener('keydown', (e) => {
                    // Ignore when user is focusing an input, textarea or button
                    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

                    if (e.code === 'Space') {
                        e.preventDefault();
                        const playBtn = document.querySelector('.bar-play-btn, .bottom-play-btn');
                        if (playBtn) playBtn.click();
                    } else if (e.key === 'm' || e.key === 'M') {
                        if (this.audio) {
                            this.setVolume(this.audio.volume > 0 ? 0 : (this.userVolume || 0.5));
                            const slider = document.querySelector('.bar-volume-slider');
                            if (slider) slider.value = this.audio.volume;
                        }
                    } else if (e.key === 'f' || e.key === 'F') {
                        this.toggleFullscreen();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        const newVol = Math.min(1, (this.audio ? this.audio.volume : this.userVolume) + 0.05);
                        this.setVolume(newVol);
                        const slider = document.querySelector('.bar-volume-slider');
                        if (slider) slider.value = newVol;
                    } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        const newVol = Math.max(0, (this.audio ? this.audio.volume : this.userVolume) - 0.05);
                        this.setVolume(newVol);
                        const slider = document.querySelector('.bar-volume-slider');
                        if (slider) slider.value = newVol;
                    }
                });

                // Zen Mode: Auto-hide HUD on idle during playback (15 seconds)
                let idleTimeout = null;
                const resetIdle = () => {
                    document.body.classList.remove('hud-idle');
                    if (idleTimeout) clearTimeout(idleTimeout);
                    if (this.audio && !this.audio.paused) {
                        idleTimeout = setTimeout(() => {
                            document.body.classList.add('hud-idle');
                        }, 15000);
                    }
                };

                ['mousemove', 'mousedown', 'keydown', 'touchstart'].forEach(evt => {
                    window.addEventListener(evt, resetIdle, { passive: true });
                });

                this.audio.addEventListener('play', resetIdle);
                this.audio.addEventListener('pause', () => {
                    document.body.classList.remove('hud-idle');
                    if (idleTimeout) clearTimeout(idleTimeout);
                });

            } else {
                console.error("Failed to find nativeLofiAudio element on screen!");
            }
        }
        return true;
    },

    startSyncTimer: function () {
        this.stopSyncTimer();
        this.initAudioContext();
        this.startVisualizer();
        this.syncInterval = setInterval(() => {
            if (this.audio && !this.audio.paused) {
                const currentTime = this.audio.currentTime;
                const duration = this.audio.duration;
                this.updateLocalUI(currentTime, duration);
            }
        }, 100); // 100ms interval for 60fps-smooth visual rendering!
    },

    stopSyncTimer: function () {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
        this.stopVisualizer();
    },

    initAudioContext: function () {
        if (!this.audioCtx && this.audio) {
            try {
                const AudioContextClass = window.AudioContext || window.webkitAudioContext;
                if (AudioContextClass) {
                    this.audioCtx = new AudioContextClass();
                    this.analyser = this.audioCtx.createAnalyser();
                    this.analyser.fftSize = 64;
                    this.analyser.smoothingTimeConstant = 0.8;
                    this.freqData = new Uint8Array(this.analyser.frequencyBinCount);
                    this.sourceNode = this.audioCtx.createMediaElementSource(this.audio);
                    this.sourceNode.connect(this.analyser);
                    this.analyser.connect(this.audioCtx.destination);
                }
            } catch (e) {
                // ponytail: Web Audio API may fail on CORS or restricted envs; add anim-fallback class
                console.warn("[lofiPlayer] Web Audio API init skipped or restricted:", e);
                const sw = document.querySelector('.sound-wave');
                if (sw) sw.classList.add('anim-fallback');
            }
        }
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            this.audioCtx.resume().catch(() => {});
        }
    },

    startVisualizer: function () {
        this.stopVisualizer();
        const bars = document.querySelectorAll('.sound-wave span');
        if (!bars || bars.length === 0 || !this.analyser) {
            const sw = document.querySelector('.sound-wave');
            if (sw) sw.classList.add('anim-fallback');
            return;
        }

        const loop = () => {
            if (this.audio && !this.audio.paused) {
                this.analyser.getByteFrequencyData(this.freqData);
                // Map low-mid frequency bands across the 4 visualizer bars
                const bands = [this.freqData[1] || 0, this.freqData[3] || 0, this.freqData[6] || 0, this.freqData[9] || 0];
                for (let i = 0; i < bars.length; i++) {
                    const val = bands[i] / 255; // 0.0 to 1.0
                    const height = Math.max(3, Math.round(val * 12));
                    bars[i].style.height = `${height}px`;
                }
                this.animFrameId = requestAnimationFrame(loop);
            } else {
                this.stopVisualizer();
            }
        };
        this.animFrameId = requestAnimationFrame(loop);
    },

    stopVisualizer: function () {
        if (this.animFrameId) {
            cancelAnimationFrame(this.animFrameId);
            this.animFrameId = null;
        }
        const bars = document.querySelectorAll('.sound-wave span');
        if (bars) {
            bars.forEach(b => b.style.height = '');
        }
    },

    updateLocalUI: function (currentTime, duration) {
        // 1. Current Time Label
        const timeLabel = document.getElementById("lofiCurrentTime");
        if (timeLabel) {
            timeLabel.textContent = this.formatTime(currentTime);
        }

        // 2. Total Duration Label
        const totalLabel = document.getElementById("lofiTotalTime");
        if (totalLabel && duration && !isNaN(duration)) {
            totalLabel.textContent = this.formatTime(duration);
        }
        
        // 3. Timeline Slider
        const slider = document.getElementById("lofiTimelineSlider");
        if (slider) {
            slider.value = currentTime;
            if (duration && !isNaN(duration)) {
                slider.max = duration;
            }
        }
        
        // 3. Left and Right Tape Rolls scale
        const leftRoll = document.getElementById("tapeRollLeft");
        const rightRoll = document.getElementById("tapeRollRight");
        if (leftRoll && rightRoll && duration > 0) {
            const p = Math.min(Math.max(currentTime / duration, 0), 1);
            const leftScale = 1.7 - (0.9 * p);
            const rightScale = 0.8 + (0.9 * p);
            leftRoll.style.transform = `scale(${leftScale})`;
            rightRoll.style.transform = `scale(${rightScale})`;
        }

        // 4. Check if title overflows container to enable slow marquee on hover
        const titleEl = document.querySelector('.bar-song-title');
        if (titleEl) {
            const hasEllipsis = titleEl.scrollWidth > titleEl.clientWidth;
            titleEl.classList.toggle('overflows', hasEllipsis);
        }
    },

    formatTime: function (seconds) {
        if (isNaN(seconds) || seconds === Infinity) return "00:00";
        const min = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);
        return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    },

    unlock: function () {
        if (this.audio) {
            console.log("Unlocking audio element synchronously via user gesture...");
            // Play a 1-microsecond silent WAV data URI to unlock the browser's media autoplay policy 
            // synchronously inside the physical mouse click event, bypassing the Blazor WebSocket async delay!
            if (!this.audio.src || this.audio.src.startsWith("data:")) {
                this.audio.src = "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA";
            }
            this.audio.play().catch(err => console.log("Audio element pre-unlocked: ", err));
        }
    },

    syncAndPlay: function (audioUrl, offsetSeconds, title, mood, artworkUrl) {
        if (!this.audio) return;
        
        const initTime = Date.now(); // Record exact call timestamp (universal UTC milliseconds)
        console.log(`Syncing audio: ${audioUrl} starting at ${offsetSeconds}s`);
        
        // Push metadata to mobile lock screen/Media Session HUD if provided
        if (title && mood && artworkUrl) {
            this.updateMetadata(title, mood, artworkUrl);
        }
        
        // Prevent reloading the audio if it's already playing the correct track
        const currentSrc = this.audio.src ? new URL(this.audio.src).pathname : '';
        const targetSrc = audioUrl.startsWith('http') ? new URL(audioUrl).pathname : audioUrl;
        
        if (this.audio.src !== audioUrl && currentSrc !== targetSrc) {
            this.audio.src = audioUrl;
            this.audio.load();
        }

        // HTML5 Audio safety guard: setting 'currentTime' on an audio element with readyState < 1 (HAVE_METADATA)
        // throws an InvalidStateError exception in many modern browsers, crashing the JavaScript execution.
        // We must defer applying drift compensation until 'loadedmetadata' fires if readyState < 1.
        if (this.audio.readyState >= 1) {
            this.applyDriftCompensation(offsetSeconds, initTime);
        } else {
            const onMetadataLoaded = () => {
                this.applyDriftCompensation(offsetSeconds, initTime);
                this.audio.removeEventListener('loadedmetadata', onMetadataLoaded);
            };
            this.audio.addEventListener('loadedmetadata', onMetadataLoaded);
        }
        
        // Browsers block play() without user interaction, so this must be triggered inside a click event handler
        this.audio.play().catch(error => {
            console.warn("Autoplay blocked or playback error:", error);
            this.dotNetRef.invokeMethodAsync('OnPlaybackStatusChanged', false);
        });
    },

    applyDriftCompensation: function (offsetSeconds, initTime) {
        try {
            const elapsedSeconds = (Date.now() - initTime) / 1000;
            const adjustedOffset = offsetSeconds + elapsedSeconds;
            const duration = this.audio.duration;
            const finalOffset = duration ? Math.min(adjustedOffset, duration - 0.1) : adjustedOffset;
            
            const currentDiff = this.audio.currentTime - finalOffset; // Negative if client is behind (lagging), positive if ahead
            const absDiff = Math.abs(currentDiff);

            if (this.audio.paused || absDiff > 4) {
                // 1. HARD JUMP: Force realign if paused or drift is major (> 4 seconds)
                console.log(`[lofiPlayer] Hard playhead drift of ${absDiff.toFixed(2)}s detected (or paused). Force realigning playhead to ${finalOffset.toFixed(2)}s`);
                this.audio.currentTime = finalOffset;
                this.audio.playbackRate = 1.0; // Reset speed
            } else if (absDiff > 0.4) {
                // 2. MICRO-PITCH SEAMLESS SYNC: Adjust playback speed by 2.5% to catch up (1.025x if lagging) or slow down (0.975x if leading)
                const speed = currentDiff < 0 ? 1.025 : 0.975;
                const driftType = currentDiff < 0 ? "lag" : "lead";
                
                this.audio.playbackRate = speed;
                console.log(`[lofiPlayer] Minor ${driftType} of ${absDiff.toFixed(2)}s. Adjusting speed to ${speed}x for seamless alignment.`);
            } else {
                // 3. IN-SYNC: Negligible drift, play at normal 1.0x speed
                this.audio.playbackRate = 1.0;
                console.log(`[lofiPlayer] Local playhead is in perfect sync (drift of ${absDiff.toFixed(2)}s is within safe 0.4s limit). Playing at 1.0x.`);
            }
            this.updateLocalUI(this.audio.currentTime, duration); // Update UI immediately
        } catch (err) {
            console.warn("Failed to apply drift compensation:", err);
        }
    },

    play: function () {
        if (this.audio) {
            this.audio.play().catch(console.error);
        }
    },

    pause: function () {
        if (this.audio) {
            this.audio.pause();
        }
    },

    setCurrentTime: function (value) {
        if (this.audio) {
            try {
                this.audio.currentTime = value;
                this.updateLocalUI(value, this.audio.duration);
            } catch (err) {
                console.warn("Failed to seek to time:", err);
            }
        }
    },

    setVolume: function (value) {
        this.userVolume = value;
        if (this.audio) {
            this.audio.volume = value;
        }
    },

    getVolume: function () {
        return this.audio ? this.audio.volume : 0.5;
    },

    updateMetadata: function (title, mood, artworkUrl) {
        if ('mediaSession' in navigator) {
            const absoluteArtworkUrl = artworkUrl.startsWith('http') 
                ? artworkUrl 
                : window.location.origin + artworkUrl;

            console.log(`[MediaSession] Updating Lockscreen Metadata: '${title}' - [${mood}] with artwork ${absoluteArtworkUrl}`);
            navigator.mediaSession.metadata = new MediaMetadata({
                title: title,
                artist: 'LofiRadio 24/7',
                album: 'Ambient Mood: ' + mood.toUpperCase(),
                artwork: [
                    { src: absoluteArtworkUrl, sizes: '512x512', type: 'image/webp' }
                ]
            });
        }
    },

    setNextTrack: function (audioUrl, title, mood, artworkUrl) {
        this.nextTrackData = {
            audioUrl: audioUrl,
            title: title,
            mood: mood,
            artworkUrl: artworkUrl
        };
        console.log(`[lofiPlayer] Next track metadata pre-loaded successfully: '${title}'`);
    },

    toggleFullscreen: function () {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.warn(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen().catch(err => {
                    console.warn(`Error attempting to exit fullscreen: ${err.message}`);
                });
            }
        }
    }
};
