using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

public class BankService : IBankService
{
    private readonly IBankRepository _bankRepository;

    public BankService(IBankRepository bankRepository)
    {
        _bankRepository = bankRepository;
    }

    public async Task<List<Bank>> GetAllBanksAsync()
    {
        return await _bankRepository.GetAllBanksAsync();
    }

    public async Task<List<Bank>> GetActiveBanksAsync()
    {
        return await _bankRepository.GetActiveBanksAsync();
    }

    public async Task<Bank?> GetBankByCodeAsync(string bankCode)
    {
        if (string.IsNullOrWhiteSpace(bankCode))
        {
            return null;
        }

        return await _bankRepository.GetBankByCodeAsync(bankCode);
    }
}
