using Radio.Application.DTOs;
using Radio.Domain.Models;

namespace Radio.Application.Services;

public interface IRadioStreamService
{
    Task<StreamStateDto?> GetCurrentStreamStateAsync(CancellationToken cancellationToken = default);
}
