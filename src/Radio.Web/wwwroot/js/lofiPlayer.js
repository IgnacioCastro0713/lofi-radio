window.lofiPlayer = {
    audio: null,
    dotNetRef: null,
    syncInterval: null,
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
                this.audio.crossOrigin = "anonymous";
                
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
                    this.dotNetRef.invokeMethodAsync('OnTrackEnded');
                    this.stopSyncTimer();
                });
                this.audio.addEventListener('error', (e) => {
                    console.error("Audio playback error:", e);
                    this.dotNetRef.invokeMethodAsync('OnPlaybackError', "Failed to load audio stream.");
                    this.stopSyncTimer();
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
        // throws an InvalidStateError exception in many modern browsers, crashing the JavaScript execution 
        // before play() is called. We must defer setting the time until 'loadedmetadata' fires if readyState < 1.
        if (this.audio.readyState >= 1) {
            try {
                const elapsedSeconds = (Date.now() - initTime) / 1000;
                const adjustedOffset = offsetSeconds + elapsedSeconds;
                const duration = this.audio.duration;
                const finalOffset = duration ? Math.min(adjustedOffset, duration - 0.1) : adjustedOffset;
                
                console.log(`Drift compensation applied directly: original offset ${offsetSeconds.toFixed(2)}s, adjusted to ${finalOffset.toFixed(2)}s`);
                this.audio.currentTime = finalOffset;
                this.updateLocalUI(finalOffset, duration); // Update UI immediately
            } catch (err) {
                console.warn("Failed to set currentTime directly:", err);
            }
        } else {
            const onMetadataLoaded = () => {
                try {
                    const elapsedSeconds = (Date.now() - initTime) / 1000;
                    const adjustedOffset = offsetSeconds + elapsedSeconds;
                    const duration = this.audio.duration;
                    const finalOffset = duration ? Math.min(adjustedOffset, duration - 0.1) : adjustedOffset;
                    
                    console.log(`Drift compensation applied on loadedmetadata: original offset ${offsetSeconds.toFixed(2)}s, adjusted to ${finalOffset.toFixed(2)}s (loading took ${elapsedSeconds.toFixed(2)}s)`);
                    this.audio.currentTime = finalOffset;
                    this.updateLocalUI(finalOffset, duration); // Update UI immediately
                } catch (err) {
                    console.warn("Failed to set currentTime inside loadedmetadata:", err);
                }
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
    }
};
