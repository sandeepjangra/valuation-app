using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IOrganizationRepository
{
    /// <summary>
    /// Get all organizations (individual documents)
    /// </summary>
    Task<List<Organization>> GetAllOrganizationsAsync();
    
    /// <summary>
    /// Get only active organizations (individual documents)
    /// </summary>
    Task<List<Organization>> GetActiveOrganizationsAsync();
    
    /// <summary>
    /// Alias for GetActiveOrganizationsAsync (for backward compatibility)
    /// </summary>
    Task<List<Organization>> GetAllActiveAsync();
    
    /// <summary>
    /// Get organization by short name
    /// </summary>
    Task<Organization?> GetByShortNameAsync(string shortName);
    
    /// <summary>
    /// Get organization by ID
    /// </summary>
    Task<Organization?> GetByIdAsync(string id);
    
    /// <summary>
    /// Increment the last reference number for an organization
    /// </summary>
    Task IncrementReferenceNumberAsync(string shortName);
    
    /// <summary>
    /// Update an organization
    /// </summary>
    Task<Organization?> UpdateAsync(Organization organization);
}
