using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

/// <summary>
/// Service interface for Report business logic
/// </summary>
public interface IReportService
{
    /// <summary>
    /// Get all reports for an organization with pagination
    /// </summary>
    Task<(List<Report> reports, long totalCount)> GetReportsAsync(
        string orgShortName, 
        string? status = null, 
        string? bankCode = null, 
        int page = 1, 
        int pageSize = 50);

    /// <summary>
    /// Get a specific report by ID
    /// </summary>
    Task<Report?> GetReportByIdAsync(string orgShortName, string reportId);

    /// <summary>
    /// Get a report by reference number
    /// </summary>
    Task<Report?> GetReportByReferenceNumberAsync(string orgShortName, string referenceNumber);

    /// <summary>
    /// Create a new report
    /// </summary>
    Task<string> CreateReportAsync(string orgShortName, Report report);

    /// <summary>
    /// Update an existing report
    /// </summary>
    Task<bool> UpdateReportAsync(string orgShortName, string reportId, Report report);

    /// <summary>
    /// Delete a report
    /// </summary>
    Task<bool> DeleteReportAsync(string orgShortName, string reportId);

    /// <summary>
    /// Submit a report for review
    /// </summary>
    Task<bool> SubmitReportAsync(string orgShortName, string reportId, string submittedBy);

    /// <summary>
    /// Get reports created by a specific user
    /// </summary>
    Task<List<Report>> GetUserReportsAsync(string orgShortName, string userEmail, int page = 1, int pageSize = 50);

    /// <summary>
    /// Get reports assigned to a specific user
    /// </summary>
    Task<List<Report>> GetAssignedReportsAsync(string orgShortName, string userEmail, int page = 1, int pageSize = 50);

    /// <summary>
    /// Generate next report ID
    /// </summary>
    Task<string> GenerateReportIdAsync(string orgShortName);
}
