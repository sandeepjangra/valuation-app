using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IBankRepository
{
    Task<List<Bank>> GetAllBanksAsync();
    Task<List<Bank>> GetActiveBanksAsync();
    Task<Bank?> GetBankByCodeAsync(string bankCode);
    Task<Bank?> GetBankByIdAsync(string bankId);
}
