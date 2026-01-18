using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Repository interface for UserProfile operations
/// UserProfiles are stored in organization-specific databases
/// </summary>
public interface IUserProfileRepository
{
    /// <summary>
    /// Get user profile by user ID
    /// </summary>
    Task<UserProfile?> GetByUserIdAsync(string orgShortName, string userId);

    /// <summary>
    /// Create a new user profile
    /// </summary>
    Task<string> CreateAsync(string orgShortName, UserProfile profile);

    /// <summary>
    /// Update user profile
    /// </summary>
    Task<bool> UpdateAsync(string orgShortName, UserProfile profile);

    /// <summary>
    /// Update last login timestamp
    /// </summary>
    Task<bool> UpdateLastLoginAsync(string orgShortName, string userId);

    /// <summary>
    /// Log user activity
    /// </summary>
    Task<bool> LogActivityAsync(string orgShortName, string userId, ActivityLog log);

    /// <summary>
    /// Get user activity logs
    /// </summary>
    Task<List<ActivityLog>> GetActivityLogsAsync(string orgShortName, string userId, int limit = 50);

    /// <summary>
    /// Increment report created count
    /// </summary>
    Task<bool> IncrementReportsCreatedAsync(string orgShortName, string userId);

    /// <summary>
    /// Increment report submitted count
    /// </summary>
    Task<bool> IncrementReportsSubmittedAsync(string orgShortName, string userId);
}
