using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Users Controller - Organization-scoped
/// Manages users within an organization context
/// </summary>
[ApiController]
[Route("api/org/{orgShortName}/users")]
public class UsersController : ControllerBase
{
    private readonly IUserManagementService _userManagementService;
    private readonly IAuthService _authService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(
        IUserManagementService userManagementService,
        IAuthService authService,
        ILogger<UsersController> logger)
    {
        _userManagementService = userManagementService;
        _authService = authService;
        _logger = logger;
    }

    /// <summary>
    /// Get all users in the organization
    /// GET /api/org/{orgShortName}/users
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetUsers(
        string orgShortName,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            _logger.LogInformation("Getting users for organization {OrgShortName}", orgShortName);

            var (users, totalCount) = await _userManagementService.GetOrganizationUsersAsync(
                orgShortName, page, pageSize);

            // Remove sensitive data
            var sanitizedUsers = users.Select(u => new
            {
                u.Id,
                u.UserId,
                u.Email,
                u.FullName,
                u.Phone,
                u.OrganizationId,
                u.OrgShortName,
                u.OrganizationName,
                u.Role,
                u.Roles,
                u.Status,
                u.IsActive,
                u.IsSystemAdmin,
                u.Department,
                u.Permissions,
                u.CreatedAt,
                u.UpdatedAt,
                u.LastLogin
            }).ToList();

            var totalPages = (int)Math.Ceiling((double)totalCount / pageSize);

            return Ok(ApiResponse<object>.SuccessResponse(
                new
                {
                    users = sanitizedUsers,
                    pagination = new
                    {
                        page,
                        pageSize,
                        totalCount,
                        totalPages,
                        hasNext = page < totalPages,
                        hasPrev = page > 1
                    }
                },
                $"Retrieved {users.Count} users"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting users for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve users. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get user details with profile
    /// GET /api/org/{orgShortName}/users/{userId}
    /// </summary>
    [HttpGet("{userId}")]
    public async Task<IActionResult> GetUser(string orgShortName, string userId)
    {
        try
        {
            _logger.LogInformation("Getting user {UserId} for organization {OrgShortName}", 
                userId, orgShortName);

            var (user, profile) = await _userManagementService.GetUserDetailsAsync(orgShortName, userId);

            if (user == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"User '{userId}' not found in organization '{orgShortName}'"
                ));
            }

            // Remove password hash
            var sanitizedUser = new
            {
                user.Id,
                user.UserId,
                user.Email,
                user.FullName,
                user.Phone,
                user.OrganizationId,
                user.OrgShortName,
                user.OrganizationName,
                user.Role,
                user.Roles,
                user.Status,
                user.IsActive,
                user.IsSystemAdmin,
                user.Department,
                user.Permissions,
                user.CreatedAt,
                user.UpdatedAt,
                user.LastLogin
            };

            return Ok(ApiResponse<object>.SuccessResponse(
                new { user = sanitizedUser, profile },
                "User retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user {UserId} for organization {OrgShortName}", 
                userId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve user. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Create a new user in the organization
    /// POST /api/org/{orgShortName}/users
    /// Requires admin role
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateUser(
        string orgShortName,
        [FromBody] CreateUserRequest request)
    {
        try
        {
            // TODO: Add authorization check for admin role
            // var currentUser = await GetCurrentUser();
            // if (!_userManagementService.IsAdmin(currentUser)) return Forbid();

            _logger.LogInformation("Creating user in organization {OrgShortName}", orgShortName);

            var user = new User
            {
                Email = request.Email,
                FullName = request.FullName,
                Phone = request.Phone,
                Role = request.Role ?? "employee",
                Roles = request.Roles ?? new List<string> { "employee" },
                Department = request.Department,
                Permissions = request.Permissions ?? new UserPermissions
                {
                    CanSubmitReports = false,
                    CanManageUsers = false,
                    IsManager = false,
                    IsAdmin = false
                }
            };

            var userId = await _userManagementService.CreateUserAsync(orgShortName, user, request.Password);

            return CreatedAtAction(
                nameof(GetUser),
                new { orgShortName, userId },
                ApiResponse<object>.SuccessResponse(
                    new { user_id = userId },
                    "User created successfully"
                )
            );
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Invalid operation while creating user in organization {OrgShortName}", 
                orgShortName);
            return BadRequest(ApiResponse<object>.ErrorResponse(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user in organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to create user. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Update user information
    /// PUT /api/org/{orgShortName}/users/{userId}
    /// Requires admin role
    /// </summary>
    [HttpPut("{userId}")]
    public async Task<IActionResult> UpdateUser(
        string orgShortName,
        string userId,
        [FromBody] UpdateUserRequest request)
    {
        try
        {
            // TODO: Add authorization check for admin role
            _logger.LogInformation("Updating user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);

            var (existingUser, _) = await _userManagementService.GetUserDetailsAsync(orgShortName, userId);
            if (existingUser == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"User '{userId}' not found"
                ));
            }

            // Update allowed fields
            if (!string.IsNullOrEmpty(request.FullName))
                existingUser.FullName = request.FullName;
            
            if (!string.IsNullOrEmpty(request.Phone))
                existingUser.Phone = request.Phone;
            
            if (!string.IsNullOrEmpty(request.Role))
                existingUser.Role = request.Role;
            
            if (request.Roles != null && request.Roles.Any())
                existingUser.Roles = request.Roles;
            
            if (!string.IsNullOrEmpty(request.Department))
                existingUser.Department = request.Department;
            
            if (request.Permissions != null)
                existingUser.Permissions = request.Permissions;

            var updated = await _userManagementService.UpdateUserAsync(orgShortName, existingUser);

            if (!updated)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"User '{userId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                new { user_id = userId },
                "User updated successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to update user. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Deactivate a user
    /// DELETE /api/org/{orgShortName}/users/{userId}
    /// Requires admin role
    /// </summary>
    [HttpDelete("{userId}")]
    public async Task<IActionResult> DeactivateUser(string orgShortName, string userId)
    {
        try
        {
            // TODO: Add authorization check for admin role
            _logger.LogInformation("Deactivating user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);

            var deactivated = await _userManagementService.DeactivateUserAsync(orgShortName, userId);

            if (!deactivated)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"User '{userId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                null,
                "User deactivated successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deactivating user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to deactivate user. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Reset user password
    /// POST /api/org/{orgShortName}/users/{userId}/reset-password
    /// Requires admin role
    /// </summary>
    [HttpPost("{userId}/reset-password")]
    public async Task<IActionResult> ResetPassword(
        string orgShortName,
        string userId,
        [FromBody] ResetPasswordRequest request)
    {
        try
        {
            // TODO: Add authorization check for admin role
            _logger.LogInformation("Resetting password for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);

            var reset = await _userManagementService.ResetPasswordAsync(orgShortName, userId, request.NewPassword);

            if (!reset)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"User '{userId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                null,
                "Password reset successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error resetting password for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to reset password. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get user activity logs
    /// GET /api/org/{orgShortName}/users/{userId}/activities
    /// </summary>
    [HttpGet("{userId}/activities")]
    public async Task<IActionResult> GetUserActivities(
        string orgShortName,
        string userId,
        [FromQuery] int limit = 50)
    {
        try
        {
            _logger.LogInformation("Getting activities for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);

            var activities = await _userManagementService.GetUserActivitiesAsync(orgShortName, userId, limit);

            return Ok(ApiResponse<object>.SuccessResponse(
                activities,
                $"Retrieved {activities.Count} activities"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities for user {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve activities. Please try again later."
            ));
        }
    }
}

/// <summary>
/// Request model for creating a user
/// </summary>
public class CreateUserRequest
{
    public string Email { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public string? Role { get; set; }
    public List<string>? Roles { get; set; }
    public string? Department { get; set; }
    public UserPermissions? Permissions { get; set; }
}

/// <summary>
/// Request model for updating a user
/// </summary>
public class UpdateUserRequest
{
    public string? FullName { get; set; }
    public string? Phone { get; set; }
    public string? Role { get; set; }
    public List<string>? Roles { get; set; }
    public string? Department { get; set; }
    public UserPermissions? Permissions { get; set; }
}

/// <summary>
/// Request model for resetting password
/// </summary>
public class ResetPasswordRequest
{
    public string NewPassword { get; set; } = string.Empty;
}
