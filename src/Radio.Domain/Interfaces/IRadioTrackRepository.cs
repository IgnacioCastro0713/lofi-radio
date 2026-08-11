using Radio.Domain.Models;

namespace Radio.Domain.Interfaces;

public interface IRadioTrackRepository
{
    Task<RadioTrack?> GetCurrentActiveTrackAsync(DateTimeOffset now, CancellationToken cancellationToken = default);
    Task<List<RadioTrack>> GetExpiredActiveTracksAsync(DateTimeOffset now, CancellationToken cancellationToken = default);
    Task<RadioTrack?> GetLastPlayedTrackAsync(CancellationToken cancellationToken = default);
    Task<RadioTrack?> GetNextTrackBySequenceAsync(long sequenceIndex, CancellationToken cancellationToken = default);
    Task<int> GetTrackCountAsync(CancellationToken cancellationToken = default);
    Task UpdateAsync(RadioTrack track, CancellationToken cancellationToken = default);
}
