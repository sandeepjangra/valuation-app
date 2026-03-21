using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface ITemplateRepository
{
    /// <summary>
    /// Get template by template ID
    /// </summary>
    /// <param name="templateId">The unique template identifier</param>
    /// <returns>Template entity or null if not found</returns>
    Task<Template?> GetTemplateByIdAsync(string templateId);
    
    /// <summary>
    /// Get template by bank code and property type
    /// </summary>
    /// <param name="bankCode">The bank code (e.g., "SBI", "HDFC")</param>
    /// <param name="propertyType">The property type (e.g., "Land", "Residential")</param>
    /// <returns>Template entity or null if not found</returns>
    Task<Template?> GetTemplateByBankAndPropertyAsync(string bankCode, string propertyType);
    
    /// <summary>
    /// Get all templates
    /// </summary>
    /// <returns>List of all template entities</returns>
    Task<List<Template>> GetAllTemplatesAsync();
    
    /// <summary>
    /// Get all templates for a specific bank
    /// </summary>
    /// <param name="bankCode">The bank code</param>
    /// <returns>List of template entities for the bank</returns>
    Task<List<Template>> GetTemplatesByBankCodeAsync(string bankCode);
    
    /// <summary>
    /// Get all active templates
    /// </summary>
    /// <returns>List of active template entities</returns>
    Task<List<Template>> GetActiveTemplatesAsync();
}

