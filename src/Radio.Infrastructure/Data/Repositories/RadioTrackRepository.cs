using Google.Cloud.Firestore;
using Radio.Domain.Interfaces;
using Radio.Domain.Models;
using Radio.Infrastructure.Data.Mappings;

namespace Radio.Infrastructure.Data.Repositories;

public class RadioTrackRepository(FirestoreDb firestoreDb, IFirestoreUnitOfWork unitOfWork) : IRadioTrackRepository
{
    public async Task<RadioTrack?> GetCurrentActiveTrackAsync(
        DateTimeOffset now,
        CancellationToken cancellationToken = default)
    {
        // Query the most recently scheduled track
        Query query = firestoreDb.Collection("radio_tracks")
            .OrderByDescending("play_start_time")
            .Limit(1);

        QuerySnapshot snapshot = await query.GetSnapshotAsync(cancellationToken);
        if (snapshot.Count > 0)
        {
            RadioTrack track = snapshot.Documents[0].ToTrack();

            // Delegate the active playback and drift buffer evaluation directly to the Rich Domain Model!
            if (track.IsActive(now))
            {
                return track;
            }
        }

        return null;
    }

    public async Task<List<RadioTrack>> GetExpiredActiveTracksAsync(
        DateTimeOffset now,
        CancellationToken cancellationToken = default)
    {
        // Expired active tracks are tracks with "playing" status whose duration has passed
        Query query = firestoreDb.Collection("radio_tracks")
            .WhereEqualTo("status", "playing");

        QuerySnapshot snapshot = await query.GetSnapshotAsync(cancellationToken);
        return snapshot.Documents.Select(doc => doc.ToTrack()).Where(track => track.IsExpired(now)).ToList();
    }

    public async Task<RadioTrack?> GetLastPlayedTrackAsync(CancellationToken cancellationToken = default)
    {
        // Fetch all tracks (max 100, blazingly fast) to perform date-based sequence tracking in memory,
        // which preserves chronological sequence memory perfectly across subsequent loop rounds!
        QuerySnapshot snapshot = await firestoreDb.Collection("radio_tracks").GetSnapshotAsync(cancellationToken);
        return snapshot.Documents
            .Select(d => d.ToTrack())
            .Where(t => t.PlayStartTime != null)
            .OrderByDescending(t => t.PlayStartTime)
            .FirstOrDefault();
    }

    public async Task<RadioTrack?> GetNextTrackBySequenceAsync(
        long sequenceIndex,
        CancellationToken cancellationToken = default)
    {
        Query query = firestoreDb.Collection("radio_tracks")
            .WhereEqualTo("sequence_index", sequenceIndex)
            .Limit(1);

        QuerySnapshot snapshot = await query.GetSnapshotAsync(cancellationToken);
        if (snapshot.Count > 0)
        {
            return snapshot.Documents[0].ToTrack();
        }

        return null;
    }

    public async Task<int> GetTrackCountAsync(CancellationToken cancellationToken = default)
    {
        AggregateQuerySnapshot snapshot = await firestoreDb.Collection("radio_tracks").Count().GetSnapshotAsync(cancellationToken);
        return (int)(snapshot.Count ?? 100);
    }

    public Task UpdateAsync(RadioTrack track, CancellationToken cancellationToken = default)
    {
        unitOfWork.PendingOperations.Add(batch =>
        {
            DocumentReference docRef = firestoreDb.Collection("radio_tracks").Document(track.Id);
            batch.Set(docRef, track.ToDictionary());
            return Task.CompletedTask;
        });
        return Task.CompletedTask;
    }
}