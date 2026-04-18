using Microsoft.Extensions.Logging;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

/// <summary>
/// Service for Report business logic
/// </summary>
public class ReportService : IReportService
{
    private readonly IReportRepository _reportRepository;
    private readonly ILogger<ReportService> _logger;

    public ReportService(IReportRepository reportRepository, ILogger<ReportService> logger)
    {
        _reportRepository = reportRepository;
        _logger = logger;
    }

    public async Task<(List<Report> reports, long totalCount)> GetReportsAsync(
        string orgShortName, 
        string? status = null, 
        string? bankCode = null, 
        int page = 1, 
        int pageSize = 50)
    {
        try
        {
            var skip = (page - 1) * pageSize;
            var reports = await _reportRepository.GetAllAsync(orgShortName, status, bankCode, skip, pageSize);
            var totalCount = await _reportRepository.GetCountAsync(orgShortName, status, bankCode);
            
            return (reports, totalCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<Report?> GetReportByIdAsync(string orgShortName, string reportId)
    {
        try
        {
            return await _reportRepository.GetByIdAsync(orgShortName, reportId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<Report?> GetReportByReferenceNumberAsync(string orgShortName, string referenceNumber)
    {
        try
        {
            return await _reportRepository.GetByReferenceNumberAsync(orgShortName, referenceNumber);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting report by reference {ReferenceNumber} for organization {OrgShortName}", 
                referenceNumber, orgShortName);
            throw;
        }
    }

    public async Task<string> CreateReportAsync(string orgShortName, Report report)
    {
        try
        {
            // Generate report ID if not provided
            if (string.IsNullOrEmpty(report.ReportId))
            {
                report.ReportId = await GenerateReportIdAsync(orgShortName);
            }

            // Set organization context
            report.OrgShortName = orgShortName;

            // Initialize workflow if not provided
            if (report.Workflow == null)
            {
                report.Workflow = new ReportWorkflow
                {
                    Status = "DRAFT"
                };
            }

            return await _reportRepository.CreateAsync(orgShortName, report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating report for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateReportAsync(string orgShortName, string reportId, Report report)
    {
        try
        {
            var existingReport = await _reportRepository.GetByIdAsync(orgShortName, reportId);
            if (existingReport == null)
            {
                _logger.LogWarning("Report {ReportId} not found in organization {OrgShortName}", reportId, orgShortName);
                return false;
            }

            return await _reportRepository.UpdateAsync(orgShortName, reportId, report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> DeleteReportAsync(string orgShortName, string reportId)
    {
        try
        {
            return await _reportRepository.DeleteAsync(orgShortName, reportId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> SubmitReportAsync(string orgShortName, string reportId, string submittedBy)
    {
        try
        {
            var report = await _reportRepository.GetByIdAsync(orgShortName, reportId);
            if (report == null)
            {
                _logger.LogWarning("Report {ReportId} not found in organization {OrgShortName}", reportId, orgShortName);
                return false;
            }

            // Update report status and workflow
            report.Status = "submitted";
            report.SubmittedAt = DateTime.UtcNow;
            
            if (report.Workflow == null)
            {
                report.Workflow = new ReportWorkflow();
            }

            report.Workflow.Status = "SUBMITTED";
            report.Workflow.SubmittedBy = submittedBy;
            report.Workflow.SubmittedAt = DateTime.UtcNow;

            return await _reportRepository.UpdateAsync(orgShortName, reportId, report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error submitting report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> ApproveReportAsync(string orgShortName, string reportId, string approvedBy)
    {
        try
        {
            _logger.LogInformation("Approving report {ReportId} for organization {OrgShortName} by {ApprovedBy}", 
                reportId, orgShortName, approvedBy);

            var report = await _reportRepository.GetByIdAsync(orgShortName, reportId);

            if (report == null)
            {
                _logger.LogWarning("Report {ReportId} not found in organization {OrgShortName}", reportId, orgShortName);
                return false;
            }

            // Validate report is submitted
            if (report.Status != "submitted")
            {
                _logger.LogWarning("Report {ReportId} cannot be approved - current status: {Status}", 
                    reportId, report.Status);
                throw new InvalidOperationException($"Report must be in 'submitted' status to be approved. Current status: {report.Status}");
            }

            // Update report status and workflow
            report.Status = "approved";
            report.CompletedAt = DateTime.UtcNow;
            report.UpdatedAt = DateTime.UtcNow;
            
            if (report.Workflow == null)
            {
                report.Workflow = new ReportWorkflow();
            }

            report.Workflow.Status = "APPROVED";
            report.Workflow.ApprovedBy = approvedBy;
            report.Workflow.ApprovedAt = DateTime.UtcNow;

            var updated = await _reportRepository.UpdateAsync(orgShortName, reportId, report);
            
            if (updated)
            {
                _logger.LogInformation("✅ Report {ReportId} approved successfully by {ApprovedBy}", 
                    reportId, approvedBy);
            }

            return updated;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error approving report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> RejectReportAsync(string orgShortName, string reportId, string rejectedBy, string rejectionReason)
    {
        try
        {
            _logger.LogInformation("Rejecting report {ReportId} for organization {OrgShortName} by {RejectedBy}", 
                reportId, orgShortName, rejectedBy);

            var report = await _reportRepository.GetByIdAsync(orgShortName, reportId);

            if (report == null)
            {
                _logger.LogWarning("Report {ReportId} not found in organization {OrgShortName}", reportId, orgShortName);
                return false;
            }

            // Validate report is submitted
            if (report.Status != "submitted")
            {
                _logger.LogWarning("Report {ReportId} cannot be rejected - current status: {Status}", 
                    reportId, report.Status);
                throw new InvalidOperationException($"Report must be in 'submitted' status to be rejected. Current status: {report.Status}");
            }

            // Update report status and workflow
            report.Status = "rejected";
            report.UpdatedAt = DateTime.UtcNow;
            
            if (report.Workflow == null)
            {
                report.Workflow = new ReportWorkflow();
            }

            report.Workflow.Status = "REJECTED";
            report.Workflow.ReviewedBy = rejectedBy;
            report.Workflow.ReviewedAt = DateTime.UtcNow;
            report.Workflow.RejectionReason = rejectionReason;

            var updated = await _reportRepository.UpdateAsync(orgShortName, reportId, report);
            
            if (updated)
            {
                _logger.LogInformation("✅ Report {ReportId} rejected by {RejectedBy}. Reason: {Reason}", 
                    reportId, rejectedBy, rejectionReason);
            }

            return updated;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error rejecting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            throw;
        }
    }

    public async Task<List<Report>> GetUserReportsAsync(string orgShortName, string userEmail, int page = 1, int pageSize = 50)
    {
        try
        {
            var skip = (page - 1) * pageSize;
            return await _reportRepository.GetByCreatedByAsync(orgShortName, userEmail, skip, pageSize);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports for user {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);
            throw;
        }
    }

    public async Task<List<Report>> GetAssignedReportsAsync(string orgShortName, string userEmail, int page = 1, int pageSize = 50)
    {
        try
        {
            var skip = (page - 1) * pageSize;
            return await _reportRepository.GetByAssignedToAsync(orgShortName, userEmail, skip, pageSize);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting assigned reports for user {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);
            throw;
        }
    }

    public async Task<string> GenerateReportIdAsync(string orgShortName)
    {
        // Generate a unique report ID with format: rpt_{timestamp}_{random}
        var timestamp = DateTime.UtcNow.ToString("yyMMddHHmmss");
        var random = Guid.NewGuid().ToString("N").Substring(0, 8);
        return $"rpt_{timestamp}_{random}";
    }
}
