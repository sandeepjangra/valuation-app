using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Repository interface for Report operations
/// Reports are stored in organization-specific databases
/// </summary>
public interface IReportRepository
{
    /// <summary>
    /// Get all reports for an organization with optional filtering
    /// </summary>
    Task<List<Report>> GetAllAsync(string orgShortName, string? status = null, string? bankCode = null, int skip = 0, int limit = 50);

    /// <summary>
    /// Get total count of reports for an organization
    /// </summary>
    Task<long> GetCountAsync(string orgShortName, string? status = null, string? bankCode = null);

    /// <summary>
    /// Get a specific report by ID
    /// </summary>
    Task<Report?> GetByIdAsync(string orgShortName, string reportId);

    /// <summary>
    /// Get a report by reference number
    /// </summary>
    Task<Report?> GetByReferenceNumberAsync(string orgShortName, string referenceNumber);

    /// <summary>
    /// Create a new report
    /// </summary>
    Task<string> CreateAsync(string orgShortName, Report report);

    /// <summary>
    /// Update an existing report
    /// </summary>
    Task<bool> UpdateAsync(string orgShortName, string reportId, Report report);

    /// <summary>
    /// Delete a report
    /// </summary>
    Task<bool> DeleteAsync(string orgShortName, string reportId);

    /// <summary>
    /// Update report status
    /// </summary>
    Task<bool> UpdateStatusAsync(string orgShortName, string reportId, string status);

    /// <summary>
    /// Get reports created by a specific user
    /// </summary>
    Task<List<Report>> GetByCreatedByAsync(string orgShortName, string userEmail, int skip = 0, int limit = 50);

    /// <summary>
    /// Get reports assigned to a specific user
    /// </summary>
    Task<List<Report>> GetByAssignedToAsync(string orgShortName, string userEmail, int skip = 0, int limit = 50);
}
