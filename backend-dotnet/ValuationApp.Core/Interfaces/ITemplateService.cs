using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface ITemplateService
{
    /// <summary>
    /// Get template for a specific bank and property type
    /// </summary>
    /// <param name="bankCode">The bank code (e.g., "SBI", "HDFC")</param>
    /// <param name="propertyType">The property type (e.g., "Land", "Residential")</param>
    /// <returns>Complete template entity or null if not found</returns>
    Task<Template?> GetTemplateAsync(string bankCode, string propertyType);
    
    /// <summary>
    /// Get template by template ID
    /// </summary>
    /// <param name="templateId">The unique template identifier</param>
    /// <returns>Template entity or null if not found</returns>
    Task<Template?> GetTemplateByIdAsync(string templateId);
    
    /// <summary>
    /// Get all templates for a specific bank
    /// </summary>
    /// <param name="bankCode">The bank code</param>
    /// <returns>List of templates for the bank</returns>
    Task<List<Template>> GetTemplatesByBankCodeAsync(string bankCode);
    
    /// <summary>
    /// Get all active templates
    /// </summary>
    /// <returns>List of all active templates</returns>
    Task<List<Template>> GetActiveTemplatesAsync();
}
