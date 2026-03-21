using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

public class TemplateRepository : ITemplateRepository
{
    private readonly IMongoCollection<Template> _templatesCollection;

    public TemplateRepository(MongoDbContext context)
    {
        _templatesCollection = context.TemplatesDatabase.GetCollection<Template>("templates");
    }

    public async Task<Template?> GetTemplateByIdAsync(string templateId)
    {
        return await _templatesCollection
            .Find(t => t.TemplateId == templateId)
            .FirstOrDefaultAsync();
    }

    public async Task<Template?> GetTemplateByBankAndPropertyAsync(string bankCode, string propertyType)
    {
        var filter = Builders<Template>.Filter.And(
            Builders<Template>.Filter.Eq("BankDetails.BankCode", bankCode),
            Builders<Template>.Filter.Eq(t => t.PropertyType, propertyType)
        );
        
        return await _templatesCollection
            .Find(filter)
            .FirstOrDefaultAsync();
    }

    public async Task<List<Template>> GetAllTemplatesAsync()
    {
        return await _templatesCollection
            .Find(_ => true)
            .ToListAsync();
    }

    public async Task<List<Template>> GetTemplatesByBankCodeAsync(string bankCode)
    {
        var filter = Builders<Template>.Filter.Eq("BankDetails.BankCode", bankCode);
        
        return await _templatesCollection
            .Find(filter)
            .ToListAsync();
    }

    public async Task<List<Template>> GetActiveTemplatesAsync()
    {
        return await _templatesCollection
            .Find(t => t.IsActive)
            .ToListAsync();
    }
}

