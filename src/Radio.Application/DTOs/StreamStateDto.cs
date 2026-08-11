using Radio.Domain.Models;

namespace Radio.Application.DTOs;

public class StreamStateDto
{
    public RadioTrack Track { get; set; } = null!;
    public double OffsetSeconds { get; set; }
}
