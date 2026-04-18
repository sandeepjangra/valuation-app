namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Service for managing organization-specific databases
/// Each organization gets its own isolated MongoDB database
/// </summary>
public interface IOrganizationDatabaseService
{
    /// <summary>
    /// Create a new database for an organization
    /// Database name will be the organization's short name
    /// </summary>
    /// <param name="orgShortName">Organization short name (becomes database name)</param>
    /// <returns>True if database was created successfully</returns>
    Task<bool> CreateOrganizationDatabaseAsync(string orgShortName);

    /// <summary>
    /// Check if an organization database exists
    /// </summary>
    /// <param name="orgShortName">Organization short name</param>
    /// <returns>True if database exists</returns>
    Task<bool> DatabaseExistsAsync(string orgShortName);

    /// <summary>
    /// Initialize default collections in organization database
    /// Creates: reports, custom_templates, custom_banks, activity_logs
    /// </summary>
    /// <param name="orgShortName">Organization short name</param>
    Task InitializeOrganizationCollectionsAsync(string orgShortName);

    /// <summary>
    /// Delete an organization database (soft delete - mark as deleted)
    /// </summary>
    /// <param name="orgShortName">Organization short name</param>
    Task<bool> DeleteOrganizationDatabaseAsync(string orgShortName);
}
