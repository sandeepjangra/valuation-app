using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

public class OrganizationRepository : IOrganizationRepository
{
    private readonly IMongoCollection<Organization> _organizations;

    public OrganizationRepository(MongoDbContext context)
    {
        _organizations = context.Organizations;
    }

    public async Task<Organization?> GetByShortNameAsync(string shortName)
    {
        return await _organizations
            .Find(o => o.ShortName == shortName)
            .FirstOrDefaultAsync();
    }

    public async Task<Organization?> GetByIdAsync(string id)
    {
        return await _organizations
            .Find(o => o.Id == id)
            .FirstOrDefaultAsync();
    }

    public async Task<List<Organization>> GetAllActiveAsync()
    {
        return await _organizations
            .Find(o => o.IsActive)
            .ToListAsync();
    }

    public async Task<Organization> CreateAsync(Organization organization)
    {
        organization.CreatedAt = DateTime.UtcNow;
        organization.UpdatedAt = DateTime.UtcNow;
        await _organizations.InsertOneAsync(organization);
        return organization;
    }

    public async Task<Organization> UpdateAsync(Organization organization)
    {
        organization.UpdatedAt = DateTime.UtcNow;
        await _organizations.ReplaceOneAsync(
            o => o.Id == organization.Id,
            organization
        );
        return organization;
    }

    public async Task<bool> IncrementReferenceNumberAsync(string shortName)
    {
        var update = Builders<Organization>.Update
            .Inc(o => o.LastReferenceNumber, 1)
            .Set(o => o.UpdatedAt, DateTime.UtcNow);

        var result = await _organizations.UpdateOneAsync(
            o => o.ShortName == shortName,
            update
        );

        return result.ModifiedCount > 0;
    }
}
