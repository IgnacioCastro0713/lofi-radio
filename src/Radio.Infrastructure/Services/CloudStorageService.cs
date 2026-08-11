using Google.Cloud.Storage.V1;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Radio.Application.Interfaces;

namespace Radio.Infrastructure.Services;

public class CloudStorageService(IConfiguration configuration, ILogger<CloudStorageService> logger)
    : IStorageService
{
    public async Task<string> GetSignedUrlAsync(string fileName, TimeSpan expiry, CancellationToken cancellationToken = default)
    {
        string bucketName = configuration["GCS_BUCKET_NAME"] ?? configuration["LofiRadio:BucketName"] ?? 
            throw new InvalidOperationException("GCS Bucket Name is not configured in settings. Check 'GCS_BUCKET_NAME' or 'LofiRadio:BucketName'.");

        logger.LogInformation("Generating signed URL for {FileName} in bucket '{Bucket}' with expiry of {Expiry}...", fileName, bucketName, expiry);

        // Fetch Application Default Credentials (ADC) - standard on Cloud Run & local gcloud setups
        Google.Apis.Auth.OAuth2.GoogleCredential credential = await Google.Apis.Auth.OAuth2.GoogleCredential.GetApplicationDefaultAsync(cancellationToken);
        UrlSigner signer = UrlSigner.FromCredential(credential);

        string signedUrl = await signer.SignAsync(
            bucketName,
            fileName,
            expiry,
            HttpMethod.Get,
            cancellationToken: cancellationToken);

        return signedUrl;
    }
}
