using Microsoft.Extensions.Logging;
using MongoDB.Driver;

namespace ValuationApp.Infrastructure.Data;

/// <summary>
/// Scoped service that provides access to organization-specific databases
/// Manages database connections based on the authenticated user's organization
/// </summary>
public class OrganizationDatabaseContext : IOrganizationDatabaseContext
{
    private readonly IMongoClient _mongoClient;
    private readonly ILogger<OrganizationDatabaseContext> _logger;
    private string? _currentOrgShortName;
    private bool _isSystemAdmin;
    private IMongoDatabase? _cachedDatabase;

    public OrganizationDatabaseContext(
        MongoDbContext mongoDbContext,
        ILogger<OrganizationDatabaseContext> logger)
    {
        _mongoClient = mongoDbContext.Client;
        _logger = logger;
    }

    public void SetOrganizationContext(string orgShortName, bool isSystemAdmin)
    {
        _currentOrgShortName = orgShortName;
        _isSystemAdmin = isSystemAdmin;
        _cachedDatabase = null; // Clear cache when context changes
        
        _logger.LogDebug("Organization context set: {OrgShortName} (SystemAdmin: {IsSystemAdmin})", 
            orgShortName, isSystemAdmin);
    }

    public IMongoDatabase GetDatabase()
    {
        if (string.IsNullOrEmpty(_currentOrgShortName))
        {
            throw new InvalidOperationException(
                "Organization context has not been set. " +
                "Ensure OrganizationContextMiddleware is properly configured.");
        }

        // Return cached database if available
        if (_cachedDatabase != null)
        {
            return _cachedDatabase;
        }

        // Get database for the organization
        _cachedDatabase = _mongoClient.GetDatabase(_currentOrgShortName);
        
        _logger.LogDebug("Accessing database for organization: {OrgShortName}", _currentOrgShortName);
        
        return _cachedDatabase;
    }

    public string GetOrganizationShortName()
    {
        if (string.IsNullOrEmpty(_currentOrgShortName))
        {
            throw new InvalidOperationException("Organization context has not been set");
        }

        return _currentOrgShortName;
    }

    public bool IsSystemAdmin()
    {
        return _isSystemAdmin;
    }
}
