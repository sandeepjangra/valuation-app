using ValuationApp.Common.Helpers;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

/// <summary>
/// Authentication service implementation
/// </summary>
public class AuthService : IAuthService
{
    private readonly IUserRepository _userRepository;
    private readonly JwtHelper _jwtHelper;

    public AuthService(IUserRepository userRepository, JwtHelper jwtHelper)
    {
        _userRepository = userRepository;
        _jwtHelper = jwtHelper;
    }

    public async Task<LoginResponse> LoginAsync(LoginRequest request)
    {
        try
        {
            // Find user by email (case-insensitive)
            var user = await _userRepository.GetUserByEmailAsync(request.Email.ToLower());

            if (user == null)
            {
                return new LoginResponse
                {
                    Success = false,
                    Message = "Invalid email or password"
                };
            }

            // Check if user is active
            if (!user.IsActive)
            {
                return new LoginResponse
                {
                    Success = false,
                    Message = "User account is inactive. Please contact administrator."
                };
            }

            // Verify password
            if (!VerifyPassword(request.Password, user.PasswordHash))
            {
                return new LoginResponse
                {
                    Success = false,
                    Message = "Invalid email or password"
                };
            }

            // Update last login
            await _userRepository.UpdateLastLoginAsync(user.UserId);

            // Map user to DTO
            var userDto = MapToUserDto(user);

            // Generate tokens
            var (accessToken, idToken, refreshToken, expiresIn) = GenerateTokens(userDto, request.RememberMe);

            // Return success response
            return new LoginResponse
            {
                Success = true,
                Message = "Login successful",
                Data = new LoginData
                {
                    AccessToken = accessToken,
                    IdToken = idToken,
                    RefreshToken = refreshToken,
                    ExpiresIn = expiresIn,
                    User = userDto
                }
            };
        }
        catch (Exception ex)
        {
            // Log exception here with full details
            Console.WriteLine($"❌ Login error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            if (ex.InnerException != null)
            {
                Console.WriteLine($"Inner exception: {ex.InnerException.Message}");
            }
            return new LoginResponse
            {
                Success = false,
                Message = $"An error occurred during login: {ex.Message}"
            };
        }
    }

    public bool VerifyPassword(string password, string passwordHash)
    {
        return PasswordHelper.VerifyPassword(password, passwordHash);
    }

    public (string accessToken, string idToken, string refreshToken, int expiresIn) GenerateTokens(UserDto user, bool rememberMe)
    {
        // Extended expiry if remember me is checked
        int expiryHours = rememberMe ? 24 * 7 : 24; // 7 days vs 1 day

        var claims = new Dictionary<string, object>
        {
            { "sub", user.UserId },
            { "email", user.Email },
            { "full_name", user.FullName },
            { "role", user.Role },
            { "organization_id", user.OrganizationId },
            { "is_system_admin", user.IsSystemAdmin.ToString().ToLower() },
            { "is_active", user.IsActive.ToString().ToLower() }
        };

        // Add optional fields if they exist
        if (!string.IsNullOrEmpty(user.OrgShortName))
        {
            claims.Add("org_short_name", user.OrgShortName);
        }

        if (user.Permissions != null)
        {
            claims.Add("is_admin", user.Permissions.IsAdmin.ToString().ToLower());
            claims.Add("is_manager", user.Permissions.IsManager.ToString().ToLower());
            claims.Add("can_submit_reports", user.Permissions.CanSubmitReports.ToString().ToLower());
            claims.Add("can_manage_users", user.Permissions.CanManageUsers.ToString().ToLower());
        }

        var accessToken = _jwtHelper.GenerateAccessToken(claims, expiryHours);
        var idToken = _jwtHelper.GenerateIdToken(claims, expiryHours);
        var refreshToken = _jwtHelper.GenerateRefreshToken(claims);
        var expiresIn = expiryHours * 3600; // Convert to seconds

        return (accessToken, idToken, refreshToken, expiresIn);
    }

    private UserDto MapToUserDto(User user)
    {
        return new UserDto
        {
            Id = user.Id,
            UserId = user.UserId,
            Email = user.Email,
            FullName = user.FullName,
            OrganizationId = user.OrganizationId,
            OrgShortName = user.OrgShortName,
            OrganizationName = user.OrganizationName,
            Role = user.Role,
            Roles = user.Roles,
            Status = user.Status,
            IsActive = user.IsActive,
            IsSystemAdmin = user.IsSystemAdmin,
            Phone = user.Phone,
            Department = user.Department,
            CreatedAt = user.CreatedAt,
            LastLogin = user.LastLogin,
            Permissions = user.Permissions != null ? new UserPermissionsDto
            {
                CanSubmitReports = user.Permissions.CanSubmitReports,
                CanManageUsers = user.Permissions.CanManageUsers,
                IsManager = user.Permissions.IsManager,
                IsAdmin = user.Permissions.IsAdmin
            } : null
        };
    }
}
