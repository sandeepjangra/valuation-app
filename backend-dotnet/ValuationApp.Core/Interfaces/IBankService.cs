using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IBankService
{
    Task<List<Bank>> GetAllBanksAsync();
    Task<List<Bank>> GetActiveBanksAsync();
    Task<Bank?> GetBankByCodeAsync(string bankCode);
}
