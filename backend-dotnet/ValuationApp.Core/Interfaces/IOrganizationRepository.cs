using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IOrganizationRepository
{
    Task<Organization?> GetByShortNameAsync(string shortName);
    Task<Organization?> GetByIdAsync(string id);
    Task<List<Organization>> GetAllActiveAsync();
    Task<Organization> CreateAsync(Organization organization);
    Task<Organization> UpdateAsync(Organization organization);
    Task<bool> IncrementReferenceNumberAsync(string shortName);
}
