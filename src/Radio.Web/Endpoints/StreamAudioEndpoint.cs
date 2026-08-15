using Radio.Application.Interfaces;
using Radio.Application.Services;
using Radio.Application.DTOs;

namespace Radio.Web.Endpoints;

public class StreamAudioEndpoint : IEndpoint
{
    public void MapEndpoint(IEndpointRouteBuilder app)
    {
        // Lightweight Live Stream State Endpoint - Allows locked mobile devices to fetch synchronized track metadata
        // directly via native HTTP fetch, bypassing throttled background WebSocket (SignalR) connections!
        app.MapGet("/api/stream/next-track", async (IRadioStreamService streamService) =>
        {
            try
            {
                StreamStateDto? state = await streamService.GetCurrentStreamStateAsync();
                if (state?.Track == null)
                {
                    return Results.NotFound("No active tracks found in the broadcast queue.");
                }

                return Results.Ok(new
                {
                    track = new
                    {
                        title = state.Track.Title,
                        mood = state.Track.Mood,
                        fileName = state.Track.FileName,
                        imagePath = state.Track.ImagePath
                    },
                    offsetSeconds = state.OffsetSeconds
                });
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[API] Error fetching next-track state: {ex}");
                Console.ResetColor();
                return Results.Problem($"Failed to fetch active stream state: {ex.Message}");
            }
        });

        // Secure Audio Signed URL Redirector - Generates a secure, temporary GCS URL and redirects the client to download directly
        app.MapGet("/api/stream/audio/{*fileName}", async (string fileName, IStorageService storageService, CancellationToken cancellationToken) =>
        {
            try
            {
                // Generate a temporary secure URL valid for 10 minutes
                string signedUrl = await storageService.GetSignedUrlAsync(fileName, TimeSpan.FromMinutes(10), cancellationToken);
                
                // Perform a 302 temporary redirect to let the browser request the file directly from Google Cloud Storage
                return Results.Redirect(signedUrl);
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[Storage Signed URL Error] Failed to generate secure URL redirect for file '{fileName}': {ex}");
                Console.ResetColor();
                return Results.Problem($"Failed to securely stream private audio via signed URL redirect: {ex.Message}");
            }
        });
    }
}
