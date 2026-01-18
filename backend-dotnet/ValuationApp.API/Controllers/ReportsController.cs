using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

/// <summary>
/// Reports Controller - Organization-scoped
/// All endpoints require organization context in route
/// </summary>
[ApiController]
[Route("api/org/{orgShortName}/reports")]
public class ReportsController : ControllerBase
{
    private readonly IReportService _reportService;
    private readonly IOrganizationService _organizationService;
    private readonly ILogger<ReportsController> _logger;

    public ReportsController(
        IReportService reportService,
        IOrganizationService organizationService,
        ILogger<ReportsController> logger)
    {
        _reportService = reportService;
        _organizationService = organizationService;
        _logger = logger;
    }

    /// <summary>
    /// Get all reports for an organization with filtering and pagination
    /// GET /api/org/{orgShortName}/reports
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetReports(
        string orgShortName,
        [FromQuery] string? status = null,
        [FromQuery] string? bankCode = null,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            _logger.LogInformation("Getting reports for organization {OrgShortName}", orgShortName);

            var (reports, totalCount) = await _reportService.GetReportsAsync(
                orgShortName, status, bankCode, page, pageSize);

            var totalPages = (int)Math.Ceiling((double)totalCount / pageSize);

            return Ok(ApiResponse<object>.SuccessResponse(
                new
                {
                    reports = reports,
                    pagination = new
                    {
                        page = page,
                        pageSize = pageSize,
                        totalCount = totalCount,
                        totalPages = totalPages,
                        hasNext = page < totalPages,
                        hasPrev = page > 1
                    }
                },
                $"Retrieved {reports.Count} reports"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve reports. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get a specific report by ID
    /// GET /api/org/{orgShortName}/reports/{reportId}
    /// </summary>
    [HttpGet("{reportId}")]
    public async Task<IActionResult> GetReport(string orgShortName, string reportId)
    {
        try
        {
            _logger.LogInformation("Getting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);

            var report = await _reportService.GetReportByIdAsync(orgShortName, reportId);

            if (report == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Report '{reportId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                report,
                "Report retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve report. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Create a new report
    /// POST /api/org/{orgShortName}/reports
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateReport(string orgShortName, [FromBody] Report report)
    {
        try
        {
            _logger.LogInformation("Creating report for organization {OrgShortName}", orgShortName);

            // Get organization ID
            var organization = await _organizationService.GetByShortNameAsync(orgShortName);
            if (organization == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Organization '{orgShortName}' not found"
                ));
            }

            report.OrganizationId = organization.Id!;
            report.OrgShortName = orgShortName;

            var reportId = await _reportService.CreateReportAsync(orgShortName, report);

            return CreatedAtAction(
                nameof(GetReport),
                new { orgShortName, reportId },
                ApiResponse<object>.SuccessResponse(
                    new { report_id = reportId },
                    "Report created successfully"
                )
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating report for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to create report. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Update an existing report
    /// PUT /api/org/{orgShortName}/reports/{reportId}
    /// </summary>
    [HttpPut("{reportId}")]
    public async Task<IActionResult> UpdateReport(
        string orgShortName, 
        string reportId, 
        [FromBody] Report report)
    {
        try
        {
            _logger.LogInformation("Updating report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);

            report.ReportId = reportId;
            report.OrgShortName = orgShortName;

            var updated = await _reportService.UpdateReportAsync(orgShortName, reportId, report);

            if (!updated)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Report '{reportId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                new { report_id = reportId },
                "Report updated successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to update report. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Delete a report
    /// DELETE /api/org/{orgShortName}/reports/{reportId}
    /// </summary>
    [HttpDelete("{reportId}")]
    public async Task<IActionResult> DeleteReport(string orgShortName, string reportId)
    {
        try
        {
            _logger.LogInformation("Deleting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);

            var deleted = await _reportService.DeleteReportAsync(orgShortName, reportId);

            if (!deleted)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Report '{reportId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                null,
                "Report deleted successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to delete report. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Submit a report for review
    /// POST /api/org/{orgShortName}/reports/{reportId}/submit
    /// </summary>
    [HttpPost("{reportId}/submit")]
    public async Task<IActionResult> SubmitReport(
        string orgShortName, 
        string reportId,
        [FromBody] SubmitReportRequest request)
    {
        try
        {
            _logger.LogInformation("Submitting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);

            var submitted = await _reportService.SubmitReportAsync(
                orgShortName, 
                reportId, 
                request.SubmittedBy);

            if (!submitted)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Report '{reportId}' not found"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                new { report_id = reportId, status = "submitted" },
                "Report submitted successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error submitting report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to submit report. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get reports created by current user
    /// GET /api/org/{orgShortName}/reports/my-reports
    /// </summary>
    [HttpGet("my-reports")]
    public async Task<IActionResult> GetMyReports(
        string orgShortName,
        [FromQuery] string userEmail,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            _logger.LogInformation("Getting reports for user {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);

            var reports = await _reportService.GetUserReportsAsync(orgShortName, userEmail, page, pageSize);

            return Ok(ApiResponse<object>.SuccessResponse(
                reports,
                $"Retrieved {reports.Count} reports"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user reports for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve user reports. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get reports assigned to current user
    /// GET /api/org/{orgShortName}/reports/assigned-to-me
    /// </summary>
    [HttpGet("assigned-to-me")]
    public async Task<IActionResult> GetAssignedReports(
        string orgShortName,
        [FromQuery] string userEmail,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            _logger.LogInformation("Getting assigned reports for user {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);

            var reports = await _reportService.GetAssignedReportsAsync(orgShortName, userEmail, page, pageSize);

            return Ok(ApiResponse<object>.SuccessResponse(
                reports,
                $"Retrieved {reports.Count} assigned reports"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting assigned reports for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve assigned reports. Please try again later."
            ));
        }
    }
}

/// <summary>
/// Request model for submitting a report
/// </summary>
public class SubmitReportRequest
{
    public string SubmittedBy { get; set; } = string.Empty;
}
