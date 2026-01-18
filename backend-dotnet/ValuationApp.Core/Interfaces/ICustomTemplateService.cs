using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Service for managing custom templates with default values
/// </summary>
public interface ICustomTemplateService
{
    /// <summary>
    /// Load template fields eligible for custom defaults
    /// Filters fields based on includeInCustomTemplate flag
    /// </summary>
    Task<CustomTemplateFieldsDto> LoadTemplateFieldsAsync(string bankCode, string propertyType);

    /// <summary>
    /// Create a new custom template
    /// </summary>
    Task<SavedCustomTemplateDto> CreateCustomTemplateAsync(CreateCustomTemplateRequest request);

    /// <summary>
    /// Get custom template by ID
    /// </summary>
    Task<SavedCustomTemplateDto?> GetCustomTemplateByIdAsync(string templateId);

    /// <summary>
    /// Update an existing custom template
    /// </summary>
    Task<SavedCustomTemplateDto> UpdateCustomTemplateAsync(string templateId, UpdateCustomTemplateRequest request);

    /// <summary>
    /// Delete custom template
    /// </summary>
    Task<bool> DeleteCustomTemplateAsync(string templateId);

    /// <summary>
    /// List all custom templates with optional filtering
    /// </summary>
    Task<List<CustomTemplateListItemDto>> ListCustomTemplatesAsync(string? bankCode = null, string? propertyType = null);

    /// <summary>
    /// Get bank name from bank code
    /// </summary>
    Task<string> GetBankNameAsync(string bankCode);
}
