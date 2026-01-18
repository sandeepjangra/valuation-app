using System.Text;
using DotNetEnv;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using ValuationApp.API.Middleware;
using ValuationApp.Common.Helpers;
using ValuationApp.Core.Interfaces;
using ValuationApp.Core.Services;
using ValuationApp.Infrastructure.Data;
using ValuationApp.Infrastructure.Repositories;
using ValuationApp.Infrastructure.Services;

// Load .env file from root directory
var envPath = Path.Combine(Directory.GetCurrentDirectory(), "..", "..", ".env");
if (File.Exists(envPath))
{
    Env.Load(envPath);
    Console.WriteLine("✅ Loaded .env file from: " + envPath);
}
else
{
    Console.WriteLine("⚠️  .env file not found at: " + envPath);
}

var builder = WebApplication.CreateBuilder(args);

// Load MongoDB connection string from environment
var mongoConnectionString = Environment.GetEnvironmentVariable("MONGODB_URI") 
    ?? builder.Configuration["MongoDbSettings:ConnectionString"];
var jwtSecret = Environment.GetEnvironmentVariable("JWT_SECRET") 
    ?? builder.Configuration["JwtSettings:Secret"];

if (string.IsNullOrEmpty(mongoConnectionString))
{
    throw new InvalidOperationException("MongoDB connection string not found in .env or appsettings.json");
}

if (string.IsNullOrEmpty(jwtSecret))
{
    throw new InvalidOperationException("JWT secret not found in .env or appsettings.json");
}

// Configure MongoDB settings
var mongoSettings = new MongoDbSettings
{
    ConnectionString = mongoConnectionString,
    AdminDatabaseName = Environment.GetEnvironmentVariable("MONGODB_ADMIN_DB_NAME") 
        ?? builder.Configuration["MongoDbSettings:AdminDatabaseName"] 
        ?? "valuation_admin",
    ReportsDatabaseName = Environment.GetEnvironmentVariable("MONGODB_REPORTS_DB_NAME") 
        ?? builder.Configuration["MongoDbSettings:ReportsDatabaseName"] 
        ?? "valuation_reports"
};

// Add MongoDB Context
builder.Services.AddSingleton(mongoSettings);
builder.Services.AddSingleton<MongoDbContext>();

// Add JWT Helper
var jwtSettings = builder.Configuration.GetSection("JwtSettings");
var jwtHelper = new JwtHelper(
    jwtSecret,
    jwtSettings["Issuer"] ?? "ValuationApp",
    jwtSettings["Audience"] ?? "ValuationApp.Frontend",
    int.Parse(jwtSettings["ExpiryHours"] ?? "24")
);
builder.Services.AddSingleton(jwtHelper);

// Add repositories and services
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IBankRepository, BankRepository>();
builder.Services.AddScoped<IBankService, BankService>();
builder.Services.AddScoped<ITemplateRepository, TemplateRepository>();
builder.Services.AddScoped<ITemplateService, TemplateService>();
builder.Services.AddScoped<IOrganizationRepository, OrganizationRepository>();
builder.Services.AddScoped<IOrganizationService, OrganizationService>();
builder.Services.AddScoped<ICustomTemplateService, CustomTemplateService>();
builder.Services.AddScoped<IReportRepository, ReportRepository>();
builder.Services.AddScoped<IReportService, ReportService>();
builder.Services.AddScoped<IUserProfileRepository, UserProfileRepository>();
builder.Services.AddScoped<IUserManagementService, UserManagementService>();
builder.Services.AddScoped<IPermissionsService, PermissionsService>();
builder.Services.AddScoped<IActivityLoggingService, ActivityLoggingService>();

// Add controllers
builder.Services.AddControllers();

// Configure CORS
var allowedOrigins = builder.Configuration.GetSection("CorsSettings:AllowedOrigins").Get<string[]>() 
    ?? new[] { "http://localhost:4200", "http://localhost:3000" };

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(allowedOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

// Add JWT Authentication
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret)),
        ValidateIssuer = true,
        ValidIssuer = jwtSettings["Issuer"] ?? "ValuationApp",
        ValidateAudience = true,
        ValidAudience = jwtSettings["Audience"] ?? "ValuationApp.Frontend",
        ValidateLifetime = true,
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

// Add Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "Valuation App API", Version = "v1" });
    
    // Add JWT authentication to Swagger
    c.AddSecurityDefinition("Bearer", new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Enter 'Bearer' [space] and then your token",
        Name = "Authorization",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement
    {
        {
            new Microsoft.OpenApi.Models.OpenApiSecurityScheme
            {
                Reference = new Microsoft.OpenApi.Models.OpenApiReference
                {
                    Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Use CORS
app.UseCors("AllowFrontend");

// Use Organization Context Middleware (after CORS, before Auth)
app.UseMiddleware<OrganizationContextMiddleware>();

// Use Authentication and Authorization
app.UseAuthentication();
app.UseAuthorization();

// Map controllers
app.MapControllers();

// Root endpoint
app.MapGet("/", () => new
{
    success = true,
    message = "Valuation App API is running",
    version = "1.0.0",
    timestamp = DateTime.UtcNow,
    endpoints = new[]
    {
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/me",
        "/api/auth/health"
    }
});

Console.WriteLine("🚀 Valuation App API Starting...");
Console.WriteLine($"📊 MongoDB: {mongoSettings.AdminDatabaseName}");
Console.WriteLine($"🔐 JWT Authentication: Enabled");
Console.WriteLine($"🌐 CORS: {string.Join(", ", allowedOrigins)}");
Console.WriteLine($"⚡ Environment: {app.Environment.EnvironmentName}");

app.Run();

