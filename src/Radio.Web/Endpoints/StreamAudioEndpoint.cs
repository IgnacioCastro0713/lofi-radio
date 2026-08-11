using Radio.Application.Interfaces;

namespace Radio.Web.Endpoints;

public class StreamAudioEndpoint : IEndpoint
{
    public void MapEndpoint(IEndpointRouteBuilder app)
    {
        // Secure Audio Signed URL Redirector - Generates a secure, temporary GCS URL and redirects the client to download directly
        app.MapGet("/api/stream/audio/{fileName}", async (string fileName, IStorageService storageService, CancellationToken cancellationToken) =>
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
