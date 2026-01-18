using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Service interface for User management with organization context
/// </summary>
public interface IUserManagementService
{
    /// <summary>
    /// Get all users in an organization with pagination
    /// </summary>
    Task<(List<User> users, long totalCount)> GetOrganizationUsersAsync(
        string orgShortName, 
        int page = 1, 
        int pageSize = 50);

    /// <summary>
    /// Get user details with profile metadata
    /// </summary>
    Task<(User? user, UserProfile? profile)> GetUserDetailsAsync(string orgShortName, string userId);

    /// <summary>
    /// Create a new user in the organization
    /// </summary>
    Task<string> CreateUserAsync(string orgShortName, User user, string password);

    /// <summary>
    /// Update user information
    /// </summary>
    Task<bool> UpdateUserAsync(string orgShortName, User user);

    /// <summary>
    /// Deactivate a user
    /// </summary>
    Task<bool> DeactivateUserAsync(string orgShortName, string userId);

    /// <summary>
    /// Reset user password
    /// </summary>
    Task<bool> ResetPasswordAsync(string orgShortName, string userId, string newPassword);

    /// <summary>
    /// Get user activity logs
    /// </summary>
    Task<List<ActivityLog>> GetUserActivitiesAsync(string orgShortName, string userId, int limit = 50);

    /// <summary>
    /// Log user activity
    /// </summary>
    Task<bool> LogUserActivityAsync(string orgShortName, string userId, string action, string? resourceType = null, string? resourceId = null, string? details = null);

    /// <summary>
    /// Update user profile
    /// </summary>
    Task<bool> UpdateUserProfileAsync(string orgShortName, string userId, UserPreferences preferences);

    /// <summary>
    /// Check if user has permission
    /// </summary>
    bool HasPermission(User user, string permission);

    /// <summary>
    /// Check if user is admin (org_admin or system_admin)
    /// </summary>
    bool IsAdmin(User user);
}
