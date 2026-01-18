using ValuationApp.Core.Entities;
using ValuationApp.Common.Models;

namespace ValuationApp.Core.Interfaces;

public interface IOrganizationService
{
    Task<Organization?> GetByShortNameAsync(string shortName);
    Task<string> GetNextReferenceNumberAsync(string shortName);
    Task<List<Organization>> GetAllActiveOrganizationsAsync();
    Task<Organization?> UpdateOrganizationAsync(string shortName, UpdateOrganizationRequest request);
}
