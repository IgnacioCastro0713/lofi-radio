using System;

namespace Radio.Domain.Models;

public class RadioTrack
{
    public string Id { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string AudioUrl { get; set; } = string.Empty;
    public double DurationSeconds { get; set; }
    public long SequenceIndex { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public string Title { get; set; } = string.Empty;
    public string Mood { get; set; } = string.Empty;
    public string ImagePath { get; set; } = string.Empty;
    public string Status { get; set; } = "queued";
    public DateTimeOffset? PlayStartTime { get; set; }


    /// <summary>
    /// Starts playback of this track at the specified UTC time.
    /// </summary>
    public void StartPlayback(DateTimeOffset startTime)
    {
        Status = "playing";
        PlayStartTime = startTime;
    }

    /// <summary>
    /// Completes the playback, transitioning status to played.
    /// </summary>
    public void Complete()
    {
        Status = "played";
    }

    /// <summary>
    /// Checks if this track is actively playing at the given UTC time, incorporating the clock-drift grace buffer.
    /// </summary>
    public bool IsActive(DateTimeOffset now)
    {
        return Status == "playing" && 
               PlayStartTime != null && 
               now >= PlayStartTime.Value.AddSeconds(-5) && // Clock-drift grace buffer
               now < PlayStartTime.Value.AddSeconds(DurationSeconds);
    }

    /// <summary>
    /// Checks if this track has completed its playing duration.
    /// </summary>
    public bool IsExpired(DateTimeOffset now)
    {
        return Status == "playing" && 
               PlayStartTime != null && 
               PlayStartTime.Value.AddSeconds(DurationSeconds) <= now;
    }

    /// <summary>
    /// Calculates the play offset in seconds with Zero Clamp safety.
    /// </summary>
    public double GetPlaybackOffset(DateTimeOffset now)
    {
        if (!IsActive(now) || PlayStartTime == null)
        {
            return 0;
        }
        double offset = (now - PlayStartTime.Value).TotalSeconds;
        return offset < 0 ? 0 : offset; // Zero Clamp Guard
    }
}
