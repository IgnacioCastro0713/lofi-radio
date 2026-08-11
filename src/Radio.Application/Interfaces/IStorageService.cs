namespace Radio.Application.Interfaces;

public interface IStorageService
{
    Task<Stream> GetAudioStreamAsync(string fileName, CancellationToken cancellationToken = default);
}
