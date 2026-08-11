namespace Radio.Application.Interfaces;

public interface IStorageService
{
    Task<string> GetSignedUrlAsync(string fileName, TimeSpan expiry, CancellationToken cancellationToken = default);
}
