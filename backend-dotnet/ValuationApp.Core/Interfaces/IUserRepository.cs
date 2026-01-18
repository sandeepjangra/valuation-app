using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Repository interface for User operations
/// </summary>
public interface IUserRepository
{
    /// <summary>
    /// Find user by email address
    /// </summary>
    Task<User?> GetUserByEmailAsync(string email);

    /// <summary>
    /// Find user by user ID
    /// </summary>
    Task<User?> GetUserByUserIdAsync(string userId);

    /// <summary>
    /// Update user's last login timestamp
    /// </summary>
    Task UpdateLastLoginAsync(string userId);

    /// <summary>
    /// Create a new user
    /// </summary>
    Task<User> CreateUserAsync(User user);

    /// <summary>
    /// Update an existing user
    /// </summary>
    Task<bool> UpdateUserAsync(User user);

    /// <summary>
    /// Get all users for a specific organization
    /// </summary>
    Task<List<User>> GetUsersByOrganizationAsync(string orgShortName, int skip = 0, int limit = 50);

    /// <summary>
    /// Get total count of users in an organization
    /// </summary>
    Task<long> GetUsersCountByOrganizationAsync(string orgShortName);

    /// <summary>
    /// Deactivate a user
    /// </summary>
    Task<bool> DeactivateUserAsync(string userId);

    /// <summary>
    /// Update user password
    /// </summary>
    Task<bool> UpdatePasswordAsync(string userId, string passwordHash);

    /// <summary>
    /// Check if email exists in organization
    /// </summary>
    Task<bool> EmailExistsInOrganizationAsync(string email, string orgShortName);
}
