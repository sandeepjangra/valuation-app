using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Authentication service interface
/// </summary>
public interface IAuthService
{
    /// <summary>
    /// Authenticate user and generate tokens
    /// </summary>
    Task<LoginResponse> LoginAsync(LoginRequest request);

    /// <summary>
    /// Verify password hash
    /// </summary>
    bool VerifyPassword(string password, string passwordHash);

    /// <summary>
    /// Generate JWT tokens for authenticated user
    /// </summary>
    (string accessToken, string idToken, string refreshToken, int expiresIn) GenerateTokens(UserDto user, bool rememberMe);
}
