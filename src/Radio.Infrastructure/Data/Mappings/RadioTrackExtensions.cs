using Google.Cloud.Firestore;
using Radio.Domain.Models;

namespace Radio.Infrastructure.Data.Mappings;

public static class RadioTrackExtensions
{
    public static RadioTrack ToTrack(this DocumentSnapshot doc)
    {
        RadioTrack track = new()
        {
            Id = doc.Id // Store the actual native Firestore Document ID string
        };

        if (doc.ContainsField("file_name")) track.FileName = doc.GetValue<string>("file_name");
        if (doc.ContainsField("audio_url")) track.AudioUrl = doc.GetValue<string>("audio_url");
        if (doc.ContainsField("duration_seconds")) track.DurationSeconds = Convert.ToDouble(doc.GetValue<object>("duration_seconds"));
        if (doc.ContainsField("sequence_index")) track.SequenceIndex = Convert.ToInt64(doc.GetValue<object>("sequence_index"));
        if (doc.ContainsField("status")) track.Status = doc.GetValue<string>("status");
        if (doc.ContainsField("title")) track.Title = doc.GetValue<string>("title");
        if (doc.ContainsField("mood")) track.Mood = doc.GetValue<string>("mood");
        
        if (doc.ContainsField("play_start_time") && doc.GetValue<object>("play_start_time") != null)
        {
            track.PlayStartTime = doc.GetValue<Timestamp>("play_start_time").ToDateTimeOffset();
        }

        if (doc.ContainsField("created_at"))
        {
            track.CreatedAt = doc.GetValue<Timestamp>("created_at").ToDateTimeOffset();
        }

        return track;
    }

    public static Dictionary<string, object> ToDictionary(this RadioTrack track)
    {
        return new Dictionary<string, object>
        {
            { "id", track.Id },
            { "file_name", track.FileName },
            { "audio_url", track.AudioUrl },
            { "duration_seconds", track.DurationSeconds },
            { "sequence_index", track.SequenceIndex },
            { "status", track.Status },
            { "play_start_time", track.PlayStartTime != null ? Timestamp.FromDateTimeOffset(track.PlayStartTime.Value) : (object)null! },
            { "created_at", Timestamp.FromDateTimeOffset(track.CreatedAt) },
            { "title", track.Title },
            { "mood", track.Mood }
        };
    }
}
