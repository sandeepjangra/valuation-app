using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Interfaces;

public interface ITemplateRepository
{
    /// <summary>
    /// Get template structure from bank-specific collection (e.g., sbi_land_property_details)
    /// </summary>
    Task<object?> GetTemplateStructureAsync(string collectionName);
    
    /// <summary>
    /// Get common form fields
    /// </summary>
    Task<object?> GetCommonFieldsAsync();
    
    /// <summary>
    /// Get document types filtered by bank and property type
    /// </summary>
    Task<List<object>> GetDocumentTypesAsync(string bankCode, string propertyType);
}
