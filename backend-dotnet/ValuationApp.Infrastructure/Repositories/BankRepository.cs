using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

public class BankRepository : IBankRepository
{
    private readonly IMongoCollection<Bank> _banksCollection;

    public BankRepository(MongoDbContext context)
    {
        // Connect to shared_resources database for banks
        var database = context.Client.GetDatabase("shared_resources");
        _banksCollection = database.GetCollection<Bank>("banks");
    }

    public async Task<List<Bank>> GetAllBanksAsync()
    {
        return await _banksCollection.Find(_ => true).ToListAsync();
    }

    public async Task<List<Bank>> GetActiveBanksAsync()
    {
        var filter = Builders<Bank>.Filter.Eq(b => b.IsActive, true);
        return await _banksCollection.Find(filter).ToListAsync();
    }

    public async Task<Bank?> GetBankByCodeAsync(string bankCode)
    {
        var filter = Builders<Bank>.Filter.Eq(b => b.BankCode, bankCode);
        return await _banksCollection.Find(filter).FirstOrDefaultAsync();
    }

    public async Task<Bank?> GetBankByIdAsync(string bankId)
    {
        var filter = Builders<Bank>.Filter.Eq(b => b.Id, bankId);
        return await _banksCollection.Find(filter).FirstOrDefaultAsync();
    }
}
