using Microsoft.Extensions.Logging;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

/// <summary>
/// Service for User management with organization context
/// </summary>
public class UserManagementService : IUserManagementService
{
    private readonly IUserRepository _userRepository;
    private readonly IUserProfileRepository _userProfileRepository;
    private readonly IOrganizationRepository _organizationRepository;
    private readonly ILogger<UserManagementService> _logger;

    public UserManagementService(
        IUserRepository userRepository,
        IUserProfileRepository userProfileRepository,
        IOrganizationRepository organizationRepository,
        ILogger<UserManagementService> logger)
    {
        _userRepository = userRepository;
        _userProfileRepository = userProfileRepository;
        _organizationRepository = organizationRepository;
        _logger = logger;
    }

    public async Task<(List<User> users, long totalCount)> GetOrganizationUsersAsync(
        string orgShortName, 
        int page = 1, 
        int pageSize = 50)
    {
        try
        {
            var skip = (page - 1) * pageSize;
            var users = await _userRepository.GetUsersByOrganizationAsync(orgShortName, skip, pageSize);
            var totalCount = await _userRepository.GetUsersCountByOrganizationAsync(orgShortName);
            
            return (users, totalCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting users for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<(User? user, UserProfile? profile)> GetUserDetailsAsync(string orgShortName, string userId)
    {
        try
        {
            var user = await _userRepository.GetUserByUserIdAsync(userId);
            if (user == null || user.OrgShortName != orgShortName)
            {
                return (null, null);
            }

            var profile = await _userProfileRepository.GetByUserIdAsync(orgShortName, userId);
            return (user, profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user details for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<string> CreateUserAsync(string orgShortName, User user, string password)
    {
        try
        {
            // Check if email already exists in organization
            var emailExists = await _userRepository.EmailExistsInOrganizationAsync(user.Email, orgShortName);
            if (emailExists)
            {
                throw new InvalidOperationException($"User with email {user.Email} already exists in organization {orgShortName}");
            }

            // Get organization to populate OrganizationId
            var organization = await _organizationRepository.GetByShortNameAsync(orgShortName);
            if (organization == null)
            {
                throw new InvalidOperationException($"Organization {orgShortName} not found");
            }

            // Generate user ID and populate fields
            user.UserId = GenerateUserId(orgShortName);
            user.OrgShortName = orgShortName;
            user.OrganizationId = organization.Id ?? string.Empty; // Populate OrganizationId
            user.Email = user.Email.ToLower();
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(password);
            user.CreatedAt = DateTime.UtcNow;
            user.UpdatedAt = DateTime.UtcNow;
            user.IsActive = true;
            user.Status = "active";

            // Create user in central database
            await _userRepository.CreateUserAsync(user);

            // Create user profile in organization database
            var profile = new UserProfile
            {
                UserId = user.UserId,
                Email = user.Email,
                OrgShortName = orgShortName,
                CreatedAt = DateTime.UtcNow
            };
            await _userProfileRepository.CreateAsync(orgShortName, profile);

            _logger.LogInformation("Created user {UserId} ({Email}) in organization {OrgShortName}", 
                user.UserId, user.Email, orgShortName);

            return user.UserId;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user in organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateUserAsync(string orgShortName, User user)
    {
        try
        {
            // Verify user belongs to organization
            var existingUser = await _userRepository.GetUserByUserIdAsync(user.UserId);
            if (existingUser == null || existingUser.OrgShortName != orgShortName)
            {
                _logger.LogWarning("User {UserId} not found in organization {OrgShortName}", 
                    user.UserId, orgShortName);
                return false;
            }

            // Don't allow changing orgShortName or userId
            user.OrgShortName = existingUser.OrgShortName;
            user.UserId = existingUser.UserId;

            return await _userRepository.UpdateUserAsync(user);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user {UserId} in organization {OrgShortName}", 
                user.UserId, orgShortName);
            throw;
        }
    }

    public async Task<bool> DeactivateUserAsync(string orgShortName, string userId)
    {
        try
        {
            // Verify user belongs to organization
            var user = await _userRepository.GetUserByUserIdAsync(userId);
            if (user == null || user.OrgShortName != orgShortName)
            {
                _logger.LogWarning("User {UserId} not found in organization {OrgShortName}", 
                    userId, orgShortName);
                return false;
            }

            var result = await _userRepository.DeactivateUserAsync(userId);
            
            if (result)
            {
                await LogUserActivityAsync(orgShortName, userId, "USER_DEACTIVATED", "user", userId, "User account deactivated");
            }

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deactivating user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<bool> ResetPasswordAsync(string orgShortName, string userId, string newPassword)
    {
        try
        {
            // Verify user belongs to organization
            var user = await _userRepository.GetUserByUserIdAsync(userId);
            if (user == null || user.OrgShortName != orgShortName)
            {
                _logger.LogWarning("User {UserId} not found in organization {OrgShortName}", 
                    userId, orgShortName);
                return false;
            }

            var passwordHash = BCrypt.Net.BCrypt.HashPassword(newPassword);
            var result = await _userRepository.UpdatePasswordAsync(userId, passwordHash);

            if (result)
            {
                await LogUserActivityAsync(orgShortName, userId, "PASSWORD_RESET", "user", userId, "Password was reset");
            }

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error resetting password for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<List<ActivityLog>> GetUserActivitiesAsync(string orgShortName, string userId, int limit = 50)
    {
        try
        {
            return await _userProfileRepository.GetActivityLogsAsync(orgShortName, userId, limit);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<bool> LogUserActivityAsync(
        string orgShortName, 
        string userId, 
        string action, 
        string? resourceType = null, 
        string? resourceId = null, 
        string? details = null)
    {
        try
        {
            var log = new ActivityLog
            {
                Action = action,
                ResourceType = resourceType,
                ResourceId = resourceId,
                Details = details,
                Timestamp = DateTime.UtcNow
            };

            return await _userProfileRepository.LogActivityAsync(orgShortName, userId, log);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error logging activity for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            // Don't throw - logging should not break the main flow
            return false;
        }
    }

    public async Task<bool> UpdateUserProfileAsync(string orgShortName, string userId, UserPreferences preferences)
    {
        try
        {
            var profile = await _userProfileRepository.GetByUserIdAsync(orgShortName, userId);
            if (profile == null)
            {
                // Create profile if it doesn't exist
                profile = new UserProfile
                {
                    UserId = userId,
                    OrgShortName = orgShortName,
                    Preferences = preferences
                };
                await _userProfileRepository.CreateAsync(orgShortName, profile);
                return true;
            }

            profile.Preferences = preferences;
            return await _userProfileRepository.UpdateAsync(orgShortName, profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating profile for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public bool HasPermission(User user, string permission)
    {
        if (user.IsSystemAdmin)
        {
            return true; // System admin has all permissions
        }

        if (user.Permissions == null)
        {
            return false;
        }

        return permission.ToLower() switch
        {
            "submit_reports" => user.Permissions.CanSubmitReports,
            "manage_users" => user.Permissions.CanManageUsers,
            "is_manager" => user.Permissions.IsManager,
            "is_admin" => user.Permissions.IsAdmin,
            _ => false
        };
    }

    public bool IsAdmin(User user)
    {
        return user.IsSystemAdmin || 
               user.Role.Equals("org_admin", StringComparison.OrdinalIgnoreCase) ||
               user.Roles.Contains("org_admin") ||
               (user.Permissions?.IsAdmin ?? false);
    }

    private string GenerateUserId(string orgShortName)
    {
        var prefix = orgShortName.Replace("-", "_").ToLower();
        var timestamp = DateTime.UtcNow.ToString("yyMMddHHmmss");
        var random = Guid.NewGuid().ToString("N").Substring(0, 6);
        return $"user_{prefix}_{timestamp}_{random}";
    }
}
