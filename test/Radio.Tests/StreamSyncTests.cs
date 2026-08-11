using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Radio.Application.DTOs;
using Radio.Application.Services;
using Radio.Domain.Interfaces;
using Radio.Domain.Models;
using Xunit;

namespace Radio.Tests;

public class FakeUnitOfWork : IUnitOfWork
{
    public List<Func<Google.Cloud.Firestore.WriteBatch, Task>> PendingOperations { get; } = new();
    public bool SaveChangesCalled { get; private set; }
    public bool TransactionBegan { get; private set; }
    public bool TransactionCommitted { get; private set; }
    public bool TransactionRolledBack { get; private set; }

    public Task BeginTransactionAsync(CancellationToken cancellationToken = default)
    {
        TransactionBegan = true;
        return Task.CompletedTask;
    }

    public Task CommitTransactionAsync(CancellationToken cancellationToken = default)
    {
        TransactionCommitted = true;
        return Task.CompletedTask;
    }

    public Task RollbackTransactionAsync(CancellationToken cancellationToken = default)
    {
        TransactionRolledBack = true;
        return Task.CompletedTask;
    }

    public Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        SaveChangesCalled = true;
        return Task.FromResult(1);
    }

    public void Dispose() { }
}

public class FakeRadioTrackRepository : IRadioTrackRepository
{
    public List<RadioTrack> Tracks { get; } = new();

    public Task<RadioTrack?> GetCurrentActiveTrackAsync(DateTimeOffset now, CancellationToken cancellationToken = default)
    {
        RadioTrack? track = Tracks
            .Where(t => t.PlayStartTime != null)
            .OrderByDescending(t => t.PlayStartTime)
            .FirstOrDefault();

        if (track != null && 
            track.PlayStartTime != null && 
            now >= track.PlayStartTime && 
            now < track.PlayStartTime.Value.AddSeconds(track.DurationSeconds))
        {
            return Task.FromResult<RadioTrack?>(track);
        }
        return Task.FromResult<RadioTrack?>(null);
    }

    public Task<List<RadioTrack>> GetExpiredActiveTracksAsync(DateTimeOffset now, CancellationToken cancellationToken = default)
    {
        var expired = Tracks
            .Where(t => t.Status == "playing" && 
                        t.PlayStartTime != null && 
                        t.PlayStartTime.Value.AddSeconds(t.DurationSeconds) <= now)
            .ToList();
        return Task.FromResult(expired);
    }

    public Task<RadioTrack?> GetLastPlayedTrackAsync(CancellationToken cancellationToken = default)
    {
        RadioTrack? track = Tracks
            .Where(t => t.PlayStartTime != null)
            .OrderByDescending(t => t.PlayStartTime)
            .FirstOrDefault();
        return Task.FromResult(track);
    }

    public Task<RadioTrack?> GetNextTrackBySequenceAsync(long sequenceIndex, CancellationToken cancellationToken = default)
    {
        RadioTrack? track = Tracks.FirstOrDefault(t => t.SequenceIndex == sequenceIndex);
        return Task.FromResult(track);
    }

    public Task<int> GetTrackCountAsync(CancellationToken cancellationToken = default)
    {
        return Task.FromResult(Tracks.Count);
    }

    public Task AddAsync(RadioTrack track, CancellationToken cancellationToken = default)
    {
        Tracks.Add(track);
        return Task.CompletedTask;
    }

    public Task UpdateAsync(RadioTrack track, CancellationToken cancellationToken = default)
    {
        var index = Tracks.FindIndex(t => t.Id == track.Id);
        if (index != -1)
        {
            Tracks[index] = track;
        }
        return Task.CompletedTask;
    }
}

public class StreamSyncTests
{
    private (FakeRadioTrackRepository Repository, FakeUnitOfWork UnitOfWork) CreateInMemoryRepository()
    {
        return (new FakeRadioTrackRepository(), new FakeUnitOfWork());
    }

    [Fact]
    public async Task GetCurrentStreamState_WhenNoTracks_ReturnsNull()
    {
        // Arrange
        (FakeRadioTrackRepository? repository, FakeUnitOfWork? unitOfWork) = CreateInMemoryRepository();
        var streamService = new RadioStreamService(repository, unitOfWork);

        // Act
        StreamStateDto? state = await streamService.GetCurrentStreamStateAsync();

        // Assert
        Assert.Null(state);
    }

    [Fact]
    public async Task GetCurrentStreamState_WhenFirstTime_ActivatesFirstQueuedTrack()
    {
        // Arrange
        (FakeRadioTrackRepository? repository, FakeUnitOfWork? unitOfWork) = CreateInMemoryRepository();
        var track = new RadioTrack
        {
            Id = "1",
            FileName = "lofi_sunset.mp3",
            AudioUrl = "/media/lofi_sunset.mp3",
            DurationSeconds = 180,
            SequenceIndex = 1,
            Status = "queued"
        };
        await repository.AddAsync(track);

        var streamService = new RadioStreamService(repository, unitOfWork);

        // Act
        StreamStateDto? state = await streamService.GetCurrentStreamStateAsync();

        // Assert
        Assert.NotNull(state);
        Assert.Equal("lofi_sunset.mp3", state.Track.FileName);
        Assert.Equal("playing", state.Track.Status);
        Assert.NotNull(state.Track.PlayStartTime);
        Assert.True(state.OffsetSeconds >= 0 && state.OffsetSeconds < 2);
    }

    [Fact]
    public async Task GetCurrentStreamState_WhenTrackActive_ReturnsCurrentTrackWithCorrectOffset()
    {
        // Arrange
        (FakeRadioTrackRepository? repository, FakeUnitOfWork? unitOfWork) = CreateInMemoryRepository();
        DateTimeOffset now = DateTimeOffset.UtcNow;
        DateTimeOffset playStartTime = now.AddSeconds(-45); // started 45s ago
        
        var track = new RadioTrack
        {
            Id = "1",
            FileName = "lofi_sunset.mp3",
            AudioUrl = "/media/lofi_sunset.mp3",
            DurationSeconds = 180,
            SequenceIndex = 1,
            Status = "playing",
            PlayStartTime = playStartTime
        };
        await repository.AddAsync(track);

        var streamService = new RadioStreamService(repository, unitOfWork);

        // Act
        StreamStateDto? state = await streamService.GetCurrentStreamStateAsync();

        // Assert
        Assert.NotNull(state);
        Assert.Equal("lofi_sunset.mp3", state.Track.FileName);
        Assert.Equal("playing", state.Track.Status);
        Assert.True(Math.Abs(state.OffsetSeconds - 45) < 1.0);
    }

    [Fact]
    public async Task GetCurrentStreamState_WhenTrackCompleted_PerformsCatchUpAndActivatesNextTrack()
    {
        // Arrange
        (FakeRadioTrackRepository? repository, FakeUnitOfWork? unitOfWork) = CreateInMemoryRepository();
        DateTimeOffset now = DateTimeOffset.UtcNow;
        DateTimeOffset track1Start = now.AddSeconds(-200); // finished 20s ago

        var track1 = new RadioTrack
        {
            Id = "1",
            FileName = "track1.mp3",
            AudioUrl = "/media/track1.mp3",
            DurationSeconds = 180,
            SequenceIndex = 1,
            Status = "playing",
            PlayStartTime = track1Start
        };
        var track2 = new RadioTrack
        {
            Id = "2",
            FileName = "track2.mp3",
            AudioUrl = "/media/track2.mp3",
            DurationSeconds = 180,
            SequenceIndex = 2,
            Status = "queued"
        };
        
        await repository.AddAsync(track1);
        await repository.AddAsync(track2);

        var streamService = new RadioStreamService(repository, unitOfWork);

        // Act
        StreamStateDto? state = await streamService.GetCurrentStreamStateAsync();

        // Assert
        Assert.NotNull(state);
        Assert.Equal("track2.mp3", state.Track.FileName);
        Assert.Equal("playing", state.Track.Status);
        Assert.True(Math.Abs(state.OffsetSeconds - 20) < 1.0);

        // Verify Track 1 was updated to "played" status
        RadioTrack dbTrack1 = repository.Tracks.First(t => t.Id == "1");
        Assert.NotNull(dbTrack1);
        Assert.Equal("played", dbTrack1.Status);
    }

    [Fact]
    public async Task GetCurrentStreamState_WhenMultipleConcurrentRequests_OnlyOneActivatesNextTrack()
    {
        // Arrange
        (FakeRadioTrackRepository? repository, FakeUnitOfWork? unitOfWork) = CreateInMemoryRepository();
        DateTimeOffset now = DateTimeOffset.UtcNow;
        DateTimeOffset track1Start = now.AddSeconds(-200); // finished 20s ago

        var track1 = new RadioTrack
        {
            Id = "1",
            FileName = "track1.mp3",
            AudioUrl = "/media/track1.mp3",
            DurationSeconds = 180,
            SequenceIndex = 1,
            Status = "playing",
            PlayStartTime = track1Start
        };
        var track2 = new RadioTrack
        {
            Id = "2",
            FileName = "track2.mp3",
            AudioUrl = "/media/track2.mp3",
            DurationSeconds = 180,
            SequenceIndex = 2,
            Status = "queued"
        };
        
        await repository.AddAsync(track1);
        await repository.AddAsync(track2);

        var streamService = new RadioStreamService(repository, unitOfWork);

        // Act - Simulate 2 concurrent requests at the same millisecond (Track 1 is completed/expired)
        Task<StreamStateDto?> task1 = streamService.GetCurrentStreamStateAsync();
        Task<StreamStateDto?> task2 = streamService.GetCurrentStreamStateAsync();

        StreamStateDto?[] results = await Task.WhenAll(task1, task2);

        // Assert - Both requests must resolve cleanly and return Track 2
        Assert.NotNull(results[0]);
        Assert.NotNull(results[1]);
        Assert.Equal("track2.mp3", results[0]!.Track.FileName);
        Assert.Equal("track2.mp3", results[1]!.Track.FileName);

        // Track 1 must be successfully marked as played, and Track 2 as playing
        Assert.Equal("played", track1.Status);
        Assert.Equal("playing", track2.Status);
        Assert.NotNull(track2.PlayStartTime);
    }
}
