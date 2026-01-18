namespace ValuationApp.Core.DTOs;

/// <summary>
/// Login response DTO
/// </summary>
public class LoginResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public LoginData? Data { get; set; }
}

/// <summary>
/// Login data containing tokens and user info
/// </summary>
public class LoginData
{
    public string AccessToken { get; set; } = string.Empty;
    public string IdToken { get; set; } = string.Empty;
    public string RefreshToken { get; set; } = string.Empty;
    public int ExpiresIn { get; set; }
    public UserDto User { get; set; } = new();
}

/// <summary>
/// User DTO for API responses
/// </summary>
public class UserDto
{
    public string? Id { get; set; }
    public string UserId { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string OrganizationId { get; set; } = string.Empty;
    public string? OrgShortName { get; set; }
    public string? OrganizationName { get; set; }
    public string Role { get; set; } = string.Empty;
    public List<string> Roles { get; set; } = new();
    public string Status { get; set; } = string.Empty;
    public bool IsActive { get; set; }
    public bool IsSystemAdmin { get; set; }
    public string? Phone { get; set; }
    public string? Department { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLogin { get; set; }
    public UserPermissionsDto? Permissions { get; set; }
}

/// <summary>
/// User permissions DTO
/// </summary>
public class UserPermissionsDto
{
    public bool CanSubmitReports { get; set; }
    public bool CanManageUsers { get; set; }
    public bool IsManager { get; set; }
    public bool IsAdmin { get; set; }
}
