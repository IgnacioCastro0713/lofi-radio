# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy MSBuild central configs first (to optimize Docker caching)
COPY ["Directory.Build.props", "./"]
COPY ["Directory.Packages.props", "./"]

# Copy project files
COPY ["src/Radio.Domain/Radio.Domain.csproj", "src/Radio.Domain/"]
COPY ["src/Radio.Application/Radio.Application.csproj", "src/Radio.Application/"]
COPY ["src/Radio.Infrastructure/Radio.Infrastructure.csproj", "src/Radio.Infrastructure/"]
COPY ["src/Radio.Web/Radio.Web.csproj", "src/Radio.Web/"]

RUN dotnet restore "src/Radio.Web/Radio.Web.csproj"

# Copy full source and publish
COPY . .
WORKDIR "/src/src/Radio.Web"
RUN dotnet publish "Radio.Web.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 2: Final Runtime
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

ENTRYPOINT ["dotnet", "Radio.Web.dll"]
