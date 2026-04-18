using MongoDB.Driver;

namespace ValuationApp.Infrastructure.Data;

/// <summary>
/// Scoped service that provides access to the current organization's database
/// Automatically determined from the authenticated user's context
/// </summary>
public interface IOrganizationDatabaseContext
{
    /// <summary>
    /// Get the MongoDB database for the current organization
    /// </summary>
    IMongoDatabase GetDatabase();

    /// <summary>
    /// Get the current organization's short name
    /// </summary>
    string GetOrganizationShortName();

    /// <summary>
    /// Check if current user is a system administrator
    /// </summary>
    bool IsSystemAdmin();

    /// <summary>
    /// Set the organization context for this request
    /// Called by middleware
    /// </summary>
    void SetOrganizationContext(string orgShortName, bool isSystemAdmin);
}
