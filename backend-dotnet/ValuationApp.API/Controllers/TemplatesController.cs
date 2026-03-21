using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TemplatesController : ControllerBase
{
    private readonly ITemplateService _templateService;
    private readonly IMapper _mapper;
    private readonly ILogger<TemplatesController> _logger;

    public TemplatesController(
        ITemplateService templateService, 
        IMapper mapper,
        ILogger<TemplatesController> logger)
    {
        _templateService = templateService;
        _mapper = mapper;
        _logger = logger;
    }

    /// <summary>
    /// Get template for a specific bank and property type
    /// </summary>
    /// <param name="bankCode">Bank code (e.g., SBI, PNB)</param>
    /// <param name="propertyType">Property type (e.g., Land, Residential)</param>
    /// <returns>Complete template with all elements and calculation rules</returns>
    [HttpGet("{bankCode}/{propertyType}")]
    public async Task<IActionResult> GetTemplate(string bankCode, string propertyType)
    {
        try
        {
            _logger.LogInformation("Fetching template for {BankCode}/{PropertyType}", bankCode, propertyType);
            
            var templateEntity = await _templateService.GetTemplateAsync(bankCode, propertyType);
            
            if (templateEntity == null)
            {
                _logger.LogWarning("Template not found for {BankCode}/{PropertyType}", bankCode, propertyType);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Template not found for bank '{bankCode}' and property type '{propertyType}'"
                ));
            }

            // Map entity to DTO
            var templateDto = _mapper.Map<ValuationTemplate>(templateEntity);

            _logger.LogInformation(
                "Successfully retrieved template {TemplateId} for {BankCode}/{PropertyType}. Elements: {ElementCount}",
                templateDto.TemplateId, bankCode, propertyType, templateDto.Elements?.Count ?? 0
            );
            
            return Ok(ApiResponse<ValuationTemplate>.SuccessResponse(
                templateDto,
                "Template retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving template for {BankCode}/{PropertyType}: {Message}", 
                bankCode, propertyType, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve template data. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get template by template ID
    /// </summary>
    /// <param name="templateId">The unique template identifier</param>
    /// <returns>Complete template</returns>
    [HttpGet("id/{templateId}")]
    public async Task<IActionResult> GetTemplateById(string templateId)
    {
        try
        {
            _logger.LogInformation("Fetching template by ID: {TemplateId}", templateId);
            
            var template = await _templateService.GetTemplateByIdAsync(templateId);
            
            if (template == null)
            {
                _logger.LogWarning("Template not found: {TemplateId}", templateId);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Template with ID '{templateId}' not found"
                ));
            }

            _logger.LogInformation("Successfully retrieved template {TemplateId}", templateId);
            
            return Ok(ApiResponse<object>.SuccessResponse(
                template,
                "Template retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving template {TemplateId}: {Message}", 
                templateId, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve template. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get all templates for a specific bank
    /// </summary>
    /// <param name="bankCode">Bank code (e.g., SBI, HDFC)</param>
    /// <returns>List of templates for the bank</returns>
    [HttpGet("bank/{bankCode}")]
    public async Task<IActionResult> GetTemplatesByBank(string bankCode)
    {
        try
        {
            _logger.LogInformation("Fetching templates for bank: {BankCode}", bankCode);
            
            var templates = await _templateService.GetTemplatesByBankCodeAsync(bankCode);
            
            _logger.LogInformation("Successfully retrieved {Count} templates for bank {BankCode}", 
                templates.Count, bankCode);
            
            return Ok(ApiResponse<object>.SuccessResponse(
                templates,
                $"Retrieved {templates.Count} templates for bank {bankCode}"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving templates for bank {BankCode}: {Message}", 
                bankCode, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve templates. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get all active templates
    /// </summary>
    /// <returns>List of all active templates</returns>
    [HttpGet("active")]
    public async Task<IActionResult> GetActiveTemplates()
    {
        try
        {
            _logger.LogInformation("Fetching all active templates");
            
            var templates = await _templateService.GetActiveTemplatesAsync();
            
            _logger.LogInformation("Successfully retrieved {Count} active templates", templates.Count);
            
            return Ok(ApiResponse<object>.SuccessResponse(
                templates,
                $"Retrieved {templates.Count} active templates"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving active templates: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve templates. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Health check endpoint for templates API
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(ApiResponse<object>.SuccessResponse(
            new { status = "healthy", service = "templates" },
            "Templates API is running"
        ));
    }
}
