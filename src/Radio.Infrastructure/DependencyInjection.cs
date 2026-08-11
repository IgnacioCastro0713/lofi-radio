using Google.Cloud.Firestore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Radio.Application.Interfaces;
using Radio.Domain.Interfaces;
using Radio.Infrastructure.Data;
using Radio.Infrastructure.Data.Repositories;
using Radio.Infrastructure.Services;

namespace Radio.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        // Register HttpClient for internal HTTP calls (Vertex AI Lyria integration)
        services.AddHttpClient();

        // Register Google Cloud FirestoreDb as a Singleton using a resilient gRPC channel with Keep-Alives
        services.AddSingleton(sp =>
        {
            string projectId = configuration["GCP_PROJECT_ID"] ?? 
                               configuration["LofiRadio:ProjectId"] ??
                               throw new InvalidOperationException("GCP Project ID is not configured.");
            
            _ = Console.ForegroundColor;
            Console.WriteLine($"[Firestore] Initializing Resilient FirestoreDb Client for Project ID: '{projectId}'");
            
            // Build a highly resilient SocketsHttpHandler with Keep-Alive pings to prevent corporate firewalls (Zscaler, Fortinet)
            // or Google Cloud Load Balancers from silently closing or resetting idle HTTP/2 gRPC connections (PROTOCOL_ERROR).
            SocketsHttpHandler handler = new SocketsHttpHandler
            {
                // Send a keepalive ping every 60 seconds of inactivity
                KeepAlivePingDelay = TimeSpan.FromSeconds(60),
                
                // Wait 30 seconds for keepalive responses before considering the connection dead
                KeepAlivePingTimeout = TimeSpan.FromSeconds(30),
                
                // Send keepalive pings even if there are no active calls on the channel (crucial to prevent resets)
                KeepAlivePingPolicy = HttpKeepAlivePingPolicy.Always,
                
                // Allow opening multiple concurrent HTTP/2 connections to prevent head-of-line blocking and handle resets gracefully
                EnableMultipleHttp2Connections = true
            };

            FirestoreDbBuilder builder = new()
            {
                ProjectId = projectId,
                GrpcAdapter = Google.Api.Gax.Grpc.GrpcNetClientAdapter.Default.WithAdditionalOptions(options =>
                {
                    options.HttpHandler = handler;
                })
            };

            return builder.Build();
        });

        // Register Unit of Work & Repositories
        services.AddScoped<IFirestoreUnitOfWork, UnitOfWork>();
        services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<IFirestoreUnitOfWork>());
        services.AddScoped<IRadioTrackRepository, RadioTrackRepository>();

        // Register Infrastructural Services
        services.AddSingleton<IStorageService, CloudStorageService>();

        return services;
    }
}
