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
        // Individual documents - one per bank (like templates)
        _banksCollection = context.TemplatesDatabase.GetCollection<Bank>("banks");
    }

    public async Task<List<Bank>> GetAllBanksAsync()
    {
        return await _banksCollection.Find(_ => true).ToListAsync();
    }

    public async Task<List<Bank>> GetActiveBanksAsync()
    {
        return await _banksCollection
            .Find(bank => bank.IsActive)
            .ToListAsync();
    }

    public async Task<Bank?> GetBankByCodeAsync(string bankCode)
    {
        return await _banksCollection
            .Find(bank => bank.BankCode == bankCode)
            .FirstOrDefaultAsync();
    }

    public async Task<Bank?> GetBankByIdAsync(string bankId)
    {
        return await _banksCollection
            .Find(bank => bank.BankId == bankId)
            .FirstOrDefaultAsync();
    }
}
