using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Permissions management endpoints
/// Handles RBAC permission templates and user permissions
/// </summary>
[ApiController]
[Route("api/permissions")]
public class PermissionsController : ControllerBase
{
    private readonly IPermissionsService _permissionsService;
    private readonly ILogger<PermissionsController> _logger;

    public PermissionsController(
        IPermissionsService permissionsService,
        ILogger<PermissionsController> logger)
    {
        _permissionsService = permissionsService;
        _logger = logger;
    }

    /// <summary>
    /// Seed permission templates (run once during setup)
    /// POST /api/permissions/seed
    /// </summary>
    [HttpPost("seed")]
    public async Task<IActionResult> SeedPermissions()
    {
        try
        {
            _logger.LogInformation("Seeding permission templates");
            
            await _permissionsService.SeedPermissionTemplatesAsync();
            
            return Ok(ApiResponse<object>.SuccessResponse(
                null,
                "Permission templates seeded successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error seeding permissions: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to seed permission templates. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get all permission templates
    /// GET /api/permissions/templates
    /// </summary>
    [HttpGet("templates")]
    public async Task<IActionResult> GetAllTemplates()
    {
        try
        {
            _logger.LogInformation("Getting all permission templates");
            
            var templates = await _permissionsService.GetAllPermissionTemplatesAsync();
            
            return Ok(ApiResponse<object>.SuccessResponse(
                templates,
                $"Retrieved {templates.Count} permission templates"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving permission templates: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve permission templates. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get permission template for specific role
    /// GET /api/permissions/templates/{role}
    /// </summary>
    [HttpGet("templates/{role}")]
    public async Task<IActionResult> GetTemplateByRole(string role)
    {
        try
        {
            _logger.LogInformation("Getting permission template for role: {Role}", role);
            
            var template = await _permissionsService.GetPermissionTemplateAsync(role);
            
            if (template == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Permission template for role '{role}' not found"
                ));
            }
            
            return Ok(ApiResponse<object>.SuccessResponse(
                template,
                "Permission template retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving permission template for role {Role}: {Message}", 
                role, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve permission template. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Health check endpoint for permissions API
    /// GET /api/permissions/health
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(ApiResponse<object>.SuccessResponse(
            new { status = "healthy", service = "permissions" },
            "Permissions API is running"
        ));
    }
}
