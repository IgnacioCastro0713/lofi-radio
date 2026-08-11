window.lofiPlayer = {
    audio: null,
    dotNetRef: null,
    syncInterval: null,
    userVolume: 0.5,       // Tracks the user's selected volume
    fadeDuration: 5,       // Duration of the fade-out effect in seconds
    fadeInDuration: 3,     // Duration of the fade-in effect in seconds

    init: function (dotNetReference) {
        this.dotNetRef = dotNetReference;
        if (!this.audio) {
            // Bind to the hidden, native HTML5 audio element on the Blazor page
            this.audio = document.getElementById("nativeLofiAudio");
            
            if (this.audio) {
                this.audio.crossOrigin = "anonymous";
                
                // Set initial volume
                this.audio.volume = this.userVolume;
                
                // Add event listeners to notify Blazor of playback changes
                this.audio.addEventListener('play', () => {
                    this.dotNetRef.invokeMethodAsync('OnPlaybackStatusChanged', true);
                });
                this.audio.addEventListener('pause', () => {
                    this.dotNetRef.invokeMethodAsync('OnPlaybackStatusChanged', false);
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

                    this.dotNetRef.invokeMethodAsync('OnTimeUpdate', currentTime, duration);
                });
                this.audio.addEventListener('ended', () => {
                    this.dotNetRef.invokeMethodAsync('OnTrackEnded');
                });
                this.audio.addEventListener('error', (e) => {
                    console.error("Audio playback error:", e);
                    this.dotNetRef.invokeMethodAsync('OnPlaybackError', "Failed to load audio stream.");
                });

                // Dynamically attach a synchronous click event listener to the play button
                setTimeout(() => {
                    const playBtn = document.querySelector(".bottom-play-btn");
                    if (playBtn) {
                        console.log("Attached synchronous autoplay unlock listener to the play button.");
                        playBtn.addEventListener('click', () => {
                            this.unlock();
                        });
                    }
                }, 100);

            } else {
                console.error("Failed to find nativeLofiAudio element on screen!");
            }
        }
        return true;
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

    syncAndPlay: function (audioUrl, offsetSeconds) {
        if (!this.audio) return;
        
        console.log(`Syncing audio: ${audioUrl} starting at ${offsetSeconds}s`);
        
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
                this.audio.currentTime = offsetSeconds;
            } catch (err) {
                console.warn("Failed to set currentTime directly:", err);
            }
        } else {
            const onMetadataLoaded = () => {
                try {
                    this.audio.currentTime = offsetSeconds;
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
    }
};
