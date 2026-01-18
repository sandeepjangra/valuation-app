using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Interfaces;

public interface ITemplateService
{
    /// <summary>
    /// Get aggregated template data for a specific bank and property type
    /// </summary>
    Task<AggregatedTemplateResponse?> GetAggregatedTemplateAsync(string bankCode, string propertyType);
}
