using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Organization-specific endpoints with org context
/// These endpoints are under /api/org/{orgShortName}/ and require valid organization
/// </summary>
[ApiController]
[Route("api/org/{orgShortName}")]
public class OrganizationScopedController : ControllerBase
{
    private readonly IOrganizationService _organizationService;
    private readonly ILogger<OrganizationScopedController> _logger;

    public OrganizationScopedController(
        IOrganizationService organizationService,
        ILogger<OrganizationScopedController> logger)
    {
        _organizationService = organizationService;
        _logger = logger;
    }

    /// <summary>
    /// Get next reference number for a report in the organization
    /// GET /api/org/{orgShortName}/next-reference-number
    /// </summary>
    /// <param name="orgShortName">Organization short name (from route)</param>
    /// <returns>Next available reference number</returns>
    [HttpGet("next-reference-number")]
    public async Task<IActionResult> GetNextReferenceNumber(string orgShortName)
    {
        try
        {
            _logger.LogInformation("Getting next reference number for organization: {OrgShortName}", orgShortName);
            
            var referenceNumber = await _organizationService.GetNextReferenceNumberAsync(orgShortName);
            
            _logger.LogInformation("Generated reference number: {ReferenceNumber}", referenceNumber);
            
            return Ok(ApiResponse<object>.SuccessResponse(
                new 
                {
                    reference_number = referenceNumber,
                    organization_short_name = orgShortName,
                    generated_at = DateTime.UtcNow
                },
                "Reference number generated successfully"
            ));
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogError(ex, "Error generating reference number for organization {OrgShortName}: {Message}", 
                orgShortName, ex.Message);
            
            return BadRequest(ApiResponse<object>.ErrorResponse(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error generating reference number for organization {OrgShortName}: {Message}", 
                orgShortName, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to generate reference number. Please try again later."
            ));
        }
    }
}
