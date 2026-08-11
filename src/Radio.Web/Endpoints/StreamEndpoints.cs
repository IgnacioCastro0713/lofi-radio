using Radio.Application.Interfaces;

namespace Radio.Web.Endpoints;

public class StreamEndpoints : IEndpoint
{
    public void MapEndpoint(IEndpointRouteBuilder app)
    {
        RouteGroupBuilder group = app.MapGroup("/api/stream");

        // Secure Audio Proxy Streamer - Streams private objects from GCS securely via Web Service Account with HTTP Range processing enabled
        group.MapGet("/audio/{fileName}", async (string fileName, IStorageService storageService, CancellationToken cancellationToken) =>
        {
            try
            {
                Stream stream = await storageService.GetAudioStreamAsync(fileName, cancellationToken);
                string contentType = fileName.EndsWith(".wav") ? "audio/wav" : "audio/mpeg";
                
                // Enable Range Processing to allow modern browsers (Chrome, Safari, iOS) to seek, buffer, and stream correctly!
                return Results.Stream(stream, contentType, enableRangeProcessing: true);
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[Storage Proxy Error] Failed to securely stream file '{fileName}' from private GCS: {ex}");
                Console.ResetColor();
                return Results.Problem($"Failed to securely stream private audio: {ex.Message}");
            }
        });
    }
}
