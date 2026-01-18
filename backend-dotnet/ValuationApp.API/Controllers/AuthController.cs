using Microsoft.AspNetCore.Mvc;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Authentication API controller
/// </summary>
[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(IAuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    /// <summary>
    /// Login endpoint
    /// POST /api/auth/login
    /// </summary>
    [HttpPost("login")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(new LoginResponse
            {
                Success = false,
                Message = "Invalid request data"
            });
        }

        _logger.LogInformation("Login attempt for email: {Email}", request.Email);

        var response = await _authService.LoginAsync(request);

        if (!response.Success)
        {
            _logger.LogWarning("Login failed for email: {Email} - {Message}", request.Email, response.Message);
            return Unauthorized(response);
        }

        _logger.LogInformation("Login successful for email: {Email}", request.Email);
        return Ok(response);
    }

    /// <summary>
    /// Logout endpoint
    /// POST /api/auth/logout
    /// </summary>
    [HttpPost("logout")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public IActionResult Logout()
    {
        // In a stateless JWT system, logout is handled client-side by removing tokens
        // Server-side logout would require token blacklisting (future enhancement)
        return Ok(new
        {
            success = true,
            message = "Logout successful"
        });
    }

    /// <summary>
    /// Get current user info (requires authentication)
    /// GET /api/auth/me
    /// </summary>
    [HttpGet("me")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public IActionResult GetCurrentUser()
    {
        // This endpoint will be protected by JWT middleware (to be added)
        // For now, return unauthorized
        return Unauthorized(new
        {
            success = false,
            message = "Authentication required"
        });
    }

    /// <summary>
    /// Health check endpoint
    /// GET /api/auth/health
    /// </summary>
    [HttpGet("health")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public IActionResult HealthCheck()
    {
        return Ok(new
        {
            success = true,
            message = "Auth API is running",
            timestamp = DateTime.UtcNow
        });
    }
}
