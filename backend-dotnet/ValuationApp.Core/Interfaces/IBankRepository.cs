using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IBankRepository
{
    /// <summary>
    /// Get all banks (individual documents)
    /// </summary>
    Task<List<Bank>> GetAllBanksAsync();
    
    /// <summary>
    /// Get only active banks (individual documents)
    /// </summary>
    Task<List<Bank>> GetActiveBanksAsync();
    
    /// <summary>
    /// Get a specific bank by bank code
    /// </summary>
    Task<Bank?> GetBankByCodeAsync(string bankCode);
    
    /// <summary>
    /// Get a specific bank by bank ID
    /// </summary>
    Task<Bank?> GetBankByIdAsync(string bankId);
}
