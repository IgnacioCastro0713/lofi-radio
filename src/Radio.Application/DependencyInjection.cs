using Microsoft.Extensions.DependencyInjection;
using Radio.Application.Services;

namespace Radio.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IRadioStreamService, RadioStreamService>();
        return services;
    }
}
