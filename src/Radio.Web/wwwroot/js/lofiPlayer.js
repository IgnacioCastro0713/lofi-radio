window.lofiPlayer = {
    audio: null,
    dotNetRef: null,
    syncInterval: null,
    nextTrackData: null,   // Pre-loaded metadata for the upcoming track to support seamless locked screen transitions
    userVolume: 0.5,       // Tracks the user's selected volume
    fadeDuration: 5,       // Duration of the fade-out effect in seconds
    fadeInDuration: 3,     // Duration of the fade-in effect in seconds
    lastUpdateTime: 0,     // Timestamp for SignalR network throttling

    init: function (dotNetReference) {
        this.dotNetRef = dotNetReference;
        if (!this.audio) {
            // Bind to the hidden, native HTML5 audio element on the Blazor page
            this.audio = document.getElementById("nativeLofiAudio");
            
            if (this.audio) {
                // Set initial volume
                this.audio.volume = this.userVolume;

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
                    // 1. Notify Blazor Server in the background so it advances its state
                    this.dotNetRef.invokeMethodAsync('OnTrackEnded');
                    
                    // 2. Transition synchronously and seamlessly in the native event context to bypass mobile lock screen blocks
                    if (this.nextTrackData) {
                        console.log(`[lofiPlayer] Synchronous seamless transition in 'ended' context to: '${this.nextTrackData.title}'`);
                        const next = this.nextTrackData;
                        this.nextTrackData = null; // Clear pre-load cache
                        this.syncAndPlay(next.audioUrl, 0, next.title, next.mood, next.artworkUrl);
                    } else {
                        this.stopSyncTimer();
                    }
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

            } else {
                console.error("Failed to find nativeLofiAudio element on screen!");
            }
        }
        return true;
    },

    startSyncTimer: function () {
        this.stopSyncTimer();
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
    },

    updateLocalUI: function (currentTime, duration) {
        // 1. Current Time Label
        const timeLabel = document.getElementById("lofiCurrentTime");
        if (timeLabel) {
            timeLabel.textContent = this.formatTime(currentTime);
        }
        
        // 2. Timeline Slider
        const slider = document.getElementById("lofiTimelineSlider");
        if (slider) {
            slider.value = currentTime;
            if (duration) {
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
    }
};
