using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Radio.Application.DTOs;
using Radio.Domain.Interfaces;
using Radio.Domain.Models;

namespace Radio.Application.Services;

public class RadioStreamService(IRadioTrackRepository repository, IUnitOfWork unitOfWork)
    : IRadioStreamService
{

    public async Task<StreamStateDto?> GetCurrentStreamStateAsync(CancellationToken cancellationToken = default)
    {
        DateTimeOffset now = DateTimeOffset.UtcNow;

        using CancellationTokenSource cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        cts.CancelAfter(TimeSpan.FromSeconds(5));

        // Use thread-safe stateful Firestore Transactions directly managed by the Unit of Work
        await unitOfWork.BeginTransactionAsync(cts.Token);
        try
        {
            // 1. Mark any expired active tracks as "played" physically in the database first
            List<RadioTrack> expiredTracks = await repository.GetExpiredActiveTracksAsync(now, cts.Token);
            foreach (RadioTrack expired in expiredTracks)
            {
                // Delegate State Transition to the Rich Domain Model!
                expired.Complete();
                await repository.UpdateAsync(expired, cts.Token);
            }
            await unitOfWork.SaveChangesAsync(cts.Token);

            // 2. Check if there is an active playing track already recorded in Firestore
            RadioTrack? activeTrack = await repository.GetCurrentActiveTrackAsync(now, cts.Token);
            if (activeTrack != null)
            {
                await unitOfWork.CommitTransactionAsync(cts.Token);
                // Calculate Playhead Offset right before returning to eliminate DB transaction latency!
                double offset = activeTrack.GetPlaybackOffset(DateTimeOffset.UtcNow);
                return new StreamStateDto { Track = activeTrack, OffsetSeconds = offset };
            }

            // 3. Perform a clean catch-up or activate the next queued track in sequence
            RadioTrack? lastPlayed = await repository.GetLastPlayedTrackAsync(cts.Token);
            long nextSequenceIndex = 1;
            DateTimeOffset nextStartTime = now;

            if (lastPlayed != null)
            {
                nextSequenceIndex = lastPlayed.SequenceIndex + 1;
                
                // Dynamically read the total track count directly from Firestore collection size (extremely robust!)
                int trackCount = await repository.GetTrackCountAsync(cts.Token);

                // Stateful Infinite Loop: If nextSequenceIndex goes beyond our dynamic track count,
                // we loop back to sequence index 1 to recycle the playlist continuously!
                if (nextSequenceIndex > trackCount)
                {
                    nextSequenceIndex = 1;
                }

                // Set nextStartTime to the exact millisecond when the last track ended to maintain seamless back-to-back continuity!
                nextStartTime = lastPlayed.PlayStartTime!.Value.AddSeconds(lastPlayed.DurationSeconds);

                // 🛡️ Future Guard Clamp: If the calculated start time is in the future (due to early track endings or client-side drifts),
                // we clamp it to 'now' to prevent negative offsets and guarantee instant active track detection!
                if (nextStartTime > now)
                {
                    nextStartTime = now;
                }

                // Delegate State Transition of the previously played track to the Rich Domain Model!
                lastPlayed.Complete();
                await repository.UpdateAsync(lastPlayed, cts.Token);
            }

            // Stateful loop to handle silent catch-ups if the station had no listeners for a while
            while (true)
            {
                // Dynamically read the total track count directly from Firestore collection size (extremely robust!)
                int trackCount = await repository.GetTrackCountAsync(cts.Token);
                
                // Inside-Loop Infinite Wrapping: If nextSequenceIndex goes beyond our dynamic track count,
                // we must loop back to 1 inside the catch-up traversal to keep catching up infinitely!
                if (nextSequenceIndex > trackCount)
                {
                    nextSequenceIndex = 1;
                }

                RadioTrack? nextTrack = await repository.GetNextTrackBySequenceAsync(nextSequenceIndex, cts.Token);
                if (nextTrack == null)
                {
                    // No more tracks in the daily loop cushion!
                    await unitOfWork.SaveChangesAsync(cts.Token);
                    await unitOfWork.CommitTransactionAsync(cts.Token);
                    return null;
                }

                // If this next track theoretically already ended in the past during quiet hours
                if (nextStartTime.AddSeconds(nextTrack.DurationSeconds) <= now)
                {
                    // Delegate State Transition to the Rich Domain Model!
                    nextTrack.Complete();
                    await repository.UpdateAsync(nextTrack, cts.Token);

                    nextStartTime = nextStartTime.AddSeconds(nextTrack.DurationSeconds);
                    nextSequenceIndex++;
                }
                else
                {
                    // Delegate State Transition and Start Playback to the Rich Domain Model!
                    nextTrack.StartPlayback(nextStartTime);
                    await repository.UpdateAsync(nextTrack, cts.Token);

                    await unitOfWork.SaveChangesAsync(cts.Token);
                    await unitOfWork.CommitTransactionAsync(cts.Token);

                    // Calculate Playhead Offset right before returning to eliminate DB transaction latency!
                    double offset = nextTrack.GetPlaybackOffset(DateTimeOffset.UtcNow);
                    
                    return new StreamStateDto { Track = nextTrack, OffsetSeconds = offset };
                }
            }
        }
        catch
        {
            await unitOfWork.RollbackTransactionAsync(cts.Token);
            throw;
        }
    }
}
