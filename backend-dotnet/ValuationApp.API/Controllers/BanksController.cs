using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class BanksController : ControllerBase
{
    private readonly IBankService _bankService;
    private readonly ILogger<BanksController> _logger;

    public BanksController(IBankService bankService, ILogger<BanksController> logger)
    {
        _bankService = bankService;
        _logger = logger;
    }

    /// <summary>
    /// Get all active banks with their templates
    /// </summary>
    /// <returns>List of active banks</returns>
    [HttpGet]
    public async Task<IActionResult> GetBanks()
    {
        try
        {
            _logger.LogInformation("Fetching all active banks");
            
            var banks = await _bankService.GetActiveBanksAsync();
            
            _logger.LogInformation("Successfully retrieved {Count} active banks", banks.Count);
            
            return Ok(banks);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving banks: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve banks. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get a specific bank by bank code
    /// </summary>
    /// <param name="bankCode">The bank code (e.g., SBI, PNB, HDFC)</param>
    /// <returns>Bank details with templates</returns>
    [HttpGet("{bankCode}")]
    public async Task<IActionResult> GetBankByCode(string bankCode)
    {
        try
        {
            _logger.LogInformation("Fetching bank with code: {BankCode}", bankCode);
            
            var bank = await _bankService.GetBankByCodeAsync(bankCode);
            
            if (bank == null)
            {
                _logger.LogWarning("Bank not found: {BankCode}", bankCode);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Bank with code '{bankCode}' not found"
                ));
            }

            _logger.LogInformation("Successfully retrieved bank: {BankName}", bank.BankName);
            
            return Ok(ApiResponse<object>.SuccessResponse(
                bank,
                "Bank retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving bank {BankCode}: {Message}", bankCode, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve bank details. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get all banks (including inactive)
    /// </summary>
    /// <returns>List of all banks</returns>
    [HttpGet("all")]
    public async Task<IActionResult> GetAllBanks()
    {
        try
        {
            _logger.LogInformation("Fetching all banks (including inactive)");
            
            var banks = await _bankService.GetAllBanksAsync();
            
            _logger.LogInformation("Successfully retrieved {Count} banks", banks.Count);
            
            return Ok(banks);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving all banks: {Message}", ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve banks. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Health check endpoint for banks API
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(ApiResponse<object>.SuccessResponse(
            new { status = "healthy", service = "banks" },
            "Banks API is running"
        ));
    }

    /// <summary>
    /// Get branches for a specific bank
    /// </summary>
    /// <param name="bankCode">The bank code (e.g., SBI, PNB, HDFC)</param>
    /// <returns>List of branches for the specified bank</returns>
    [HttpGet("{bankCode}/branches")]
    public async Task<IActionResult> GetBankBranches(string bankCode)
    {
        try
        {
            _logger.LogInformation("Fetching branches for bank: {BankCode}", bankCode);
            
            var bank = await _bankService.GetBankByCodeAsync(bankCode);
            
            if (bank == null)
            {
                _logger.LogWarning("Bank not found: {BankCode}", bankCode);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Bank with code '{bankCode}' not found"
                ));
            }

            // Return branches if available, otherwise empty list
            var branches = bank.BankBranches ?? new List<ValuationApp.Core.Entities.BankBranch>();
            
            _logger.LogInformation("Successfully retrieved {Count} branches for bank {BankName}", 
                branches.Count, bank.BankName);
            
            return Ok(branches);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving branches for bank {BankCode}: {Message}", bankCode, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve bank branches. Please try again later."
            ));
        }
    }
}
