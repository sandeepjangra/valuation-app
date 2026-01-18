using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IPermissionsService
{
    /// <summary>
    /// Get permission template for a role
    /// </summary>
    Task<PermissionTemplate?> GetPermissionTemplateAsync(string role);

    /// <summary>
    /// Get all permission templates
    /// </summary>
    Task<List<PermissionTemplate>> GetAllPermissionTemplatesAsync();

    /// <summary>
    /// Seed default permission templates (run once during setup)
    /// </summary>
    Task SeedPermissionTemplatesAsync();

    /// <summary>
    /// Check if user has specific permission
    /// </summary>
    Task<bool> HasPermissionAsync(string userId, string permission);

    /// <summary>
    /// Get user's effective permissions (role permissions + overrides)
    /// </summary>
    Task<PermissionSet> GetUserPermissionsAsync(string userId);
}
