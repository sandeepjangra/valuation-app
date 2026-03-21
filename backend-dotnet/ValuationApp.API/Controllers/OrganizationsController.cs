using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Organization management endpoints
/// These endpoints manage organizations themselves and don't require org context in route
/// </summary>
[ApiController]
[Route("api/organizations")]
public class OrganizationsController : ControllerBase
{
    private readonly IOrganizationService _organizationService;
    private readonly IMapper _mapper;
    private readonly ILogger<OrganizationsController> _logger;

    public OrganizationsController(
        IOrganizationService organizationService,
        IMapper mapper,
        ILogger<OrganizationsController> logger)
    {
        _organizationService = organizationService;
        _mapper = mapper;
        _logger = logger;
    }

    /// <summary>
    /// Get all active organizations
    /// GET /api/organizations
    /// </summary>
    /// <returns>List of active organizations</returns>
    [HttpGet]
    public async Task<IActionResult> GetAllOrganizations()
    {
        try
        {
            _logger.LogInformation("Getting all active organizations");
            
            var organizationsEntities = await _organizationService.GetAllActiveOrganizationsAsync();
            
            // Map entities to DTOs
            var organizationsDtos = _mapper.Map<List<OrganizationResponseDto>>(organizationsEntities);
            
            return Ok(ApiResponse<List<OrganizationResponseDto>>.SuccessResponse(
                organizationsDtos,
                "Organizations retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving organizations: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve organizations. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get organization details
    /// GET /api/organizations/{orgShortName}
    /// </summary>
    /// <param name="orgShortName">Organization short name</param>
    /// <returns>Organization details</returns>
    [HttpGet("{orgShortName}")]
    public async Task<IActionResult> GetOrganization(string orgShortName)
    {
        try
        {
            _logger.LogInformation("Getting organization details: {OrgShortName}", orgShortName);
            
            var organizationEntity = await _organizationService.GetByShortNameAsync(orgShortName);
            
            if (organizationEntity == null)
            {
                _logger.LogWarning("Organization not found: {OrgShortName}", orgShortName);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Organization '{orgShortName}' not found"
                ));
            }
            
            // Map entity to DTO
            var organizationDto = _mapper.Map<OrganizationResponseDto>(organizationEntity);
            
            return Ok(ApiResponse<OrganizationResponseDto>.SuccessResponse(
                organizationDto,
                "Organization retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving organization {OrgShortName}: {Message}", 
                orgShortName, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve organization details. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Update organization details
    /// PATCH /api/organizations/{orgShortName}
    /// </summary>
    /// <param name="orgShortName">Organization short name</param>
    /// <param name="request">Update request with fields to change</param>
    /// <returns>Updated organization</returns>
    [HttpPatch("{orgShortName}")]
    public async Task<IActionResult> UpdateOrganization(
        string orgShortName,
        [FromBody] UpdateOrganizationRequest request)
    {
        try
        {
            _logger.LogInformation("Updating organization: {OrgShortName}", orgShortName);

            if (request == null)
            {
                return BadRequest(ApiResponse<object>.ErrorResponse(
                    "Request body is required"
                ));
            }

            var updatedOrganization = await _organizationService.UpdateOrganizationAsync(orgShortName, request);

            if (updatedOrganization == null)
            {
                _logger.LogWarning("Organization not found for update: {OrgShortName}", orgShortName);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Organization '{orgShortName}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                updatedOrganization,
                "Organization updated successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating organization {OrgShortName}: {Message}",
                orgShortName, ex.Message);

            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to update organization. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Health check endpoint for organizations API
    /// GET /api/organizations/health
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(ApiResponse<object>.SuccessResponse(
            new { status = "healthy", service = "organizations" },
            "Organizations API is running"
        ));
    }
}

