using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

public class OrganizationRepository : IOrganizationRepository
{
    private readonly IMongoCollection<Organization> _organizationsCollection;

    public OrganizationRepository(MongoDbContext context)
    {
        // Individual documents - one per organization (like templates)
        _organizationsCollection = context.TemplatesDatabase.GetCollection<Organization>("organizations");
    }

    public async Task<Organization?> GetByShortNameAsync(string shortName)
    {
        return await _organizationsCollection
            .Find(org => org.ShortName == shortName)
            .FirstOrDefaultAsync();
    }

    public async Task<Organization?> GetByIdAsync(string id)
    {
        return await _organizationsCollection
            .Find(org => org.OrganizationId == id)
            .FirstOrDefaultAsync();
    }

    public async Task<List<Organization>> GetAllOrganizationsAsync()
    {
        return await _organizationsCollection.Find(_ => true).ToListAsync();
    }

    public async Task<List<Organization>> GetActiveOrganizationsAsync()
    {
        return await _organizationsCollection
            .Find(org => org.IsActive)
            .ToListAsync();
    }

    public async Task<List<Organization>> GetAllActiveAsync()
    {
        return await GetActiveOrganizationsAsync();
    }

    public async Task IncrementReferenceNumberAsync(string shortName)
    {
        var filter = Builders<Organization>.Filter.Eq(org => org.ShortName, shortName);
        var update = Builders<Organization>.Update
            .Inc(org => org.LastReferenceNumber, 1)
            .Set(org => org.UpdatedAt, DateTime.UtcNow);

        await _organizationsCollection.UpdateOneAsync(filter, update);
    }

    public async Task<Organization?> UpdateAsync(Organization organization)
    {
        organization.UpdatedAt = DateTime.UtcNow;

        var filter = Builders<Organization>.Filter.Eq(org => org.ShortName, organization.ShortName);
        
        await _organizationsCollection.ReplaceOneAsync(filter, organization);

        return await GetByShortNameAsync(organization.ShortName);
    }
}
