using Google.Cloud.Storage.V1;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Radio.Application.Interfaces;

namespace Radio.Infrastructure.Services;

public class CloudStorageService(IConfiguration configuration, ILogger<CloudStorageService> logger)
    : IStorageService
{
    public async Task<Stream> GetAudioStreamAsync(string fileName, CancellationToken cancellationToken = default)
    {
        string bucketName = configuration["GCS_BUCKET_NAME"] ?? configuration["LofiRadio:BucketName"] ?? 
            throw new InvalidOperationException("GCS Bucket Name is not configured in settings. Check 'GCS_BUCKET_NAME' or 'LofiRadio:BucketName'.");

        logger.LogInformation("Downloading and streaming {FileName} from private GCS Bucket '{Bucket}'...", fileName, bucketName);

        StorageClient client = await StorageClient.CreateAsync();
        MemoryStream memoryStream = new();
        
        // Securely download the private object to our memory stream using the Web SA credentials
        await client.DownloadObjectAsync(
            bucketName, 
            fileName, 
            memoryStream, 
            cancellationToken: cancellationToken);
            
        memoryStream.Position = 0; // Reset position to allow reading from start
        return memoryStream;
    }
}
