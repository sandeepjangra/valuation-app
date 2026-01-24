using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using System.Text.Json;
using MongoDB.Bson;

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

    /// <summary>
    /// Save report as draft (NO VALIDATION)
    /// POST /api/org/{orgShortName}/reports/draft
    /// Allows saving incomplete data, no field validation
    /// </summary>
    [HttpPost("draft")]
    public async Task<IActionResult> SaveDraft(string orgShortName, [FromBody] Report report)
    {
        try
        {
            _logger.LogInformation("Saving draft report for organization {OrgShortName}", orgShortName);

            // Get organization ID
            var organization = await _organizationService.GetByShortNameAsync(orgShortName);
            if (organization == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Organization '{orgShortName}' not found"
                ));
            }

            // Set required fields for draft
            report.OrganizationId = organization.Id!;
            report.OrgShortName = orgShortName;
            report.Status = "draft"; // Force draft status
            report.CreatedAt = DateTime.UtcNow;
            report.UpdatedAt = DateTime.UtcNow;
            
            // Convert JsonElement dictionaries to proper objects for MongoDB serialization
            report.ReportData = ConvertJsonElementDictionary(report.ReportData);
            report.FormData = ConvertJsonElementDictionary(report.FormData);

            // No validation - accept any data
            var reportId = await _reportService.CreateReportAsync(orgShortName, report);

            _logger.LogInformation("Draft report {ReportId} saved successfully", reportId);

            return CreatedAtAction(
                nameof(GetReport),
                new { orgShortName, reportId },
                ApiResponse<object>.SuccessResponse(
                    new { report_id = reportId, status = "draft" },
                    "Draft saved successfully"
                )
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error saving draft report for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to save draft. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Update existing draft report (NO VALIDATION)
    /// PUT /api/org/{orgShortName}/reports/draft/{reportId}
    /// </summary>
    [HttpPut("draft/{reportId}")]
    public async Task<IActionResult> UpdateDraft(
        string orgShortName, 
        string reportId, 
        [FromBody] Report report)
    {
        try
        {
            _logger.LogInformation("Updating draft report {ReportId} for organization {OrgShortName}", 
                reportId, orgShortName);

            // Verify report exists and is a draft
            var existingReport = await _reportService.GetReportByIdAsync(orgShortName, reportId);
            if (existingReport == null)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Report '{reportId}' not found"
                ));
            }

            // Merge new data into existing report to preserve _id and other system fields
            existingReport.BankCode = report.BankCode;
            existingReport.PropertyType = report.PropertyType;
            existingReport.ApplicantName = report.ApplicantName;
            
            // Convert JsonElement dictionaries to proper objects for MongoDB serialization
            existingReport.ReportData = ConvertJsonElementDictionary(report.ReportData);
            existingReport.FormData = ConvertJsonElementDictionary(report.FormData);
            
            existingReport.Status = "draft"; // Keep as draft
            existingReport.UpdatedAt = DateTime.UtcNow;

            // No validation - accept any data
            var success = await _reportService.UpdateReportAsync(orgShortName, reportId, existingReport);

            if (!success)
            {
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Failed to update report '{reportId}'"
                ));
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                new { report_id = reportId, status = "draft" },
                "Draft updated successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating draft report {ReportId}", reportId);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to update draft. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Get all draft reports for current user
    /// GET /api/org/{orgShortName}/reports/drafts
    /// </summary>
    [HttpGet("drafts")]
    public async Task<IActionResult> GetDrafts(
        string orgShortName,
        [FromQuery] string? userEmail = null,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            _logger.LogInformation("Getting draft reports for organization {OrgShortName}", orgShortName);

            var (reports, totalCount) = await _reportService.GetReportsAsync(
                orgShortName, "draft", null, page, pageSize);

            // Filter by user if email provided
            if (!string.IsNullOrEmpty(userEmail))
            {
                reports = reports.Where(r => r.CreatedByEmail == userEmail).ToList();
            }

            return Ok(ApiResponse<object>.SuccessResponse(
                new { reports, total_count = totalCount },
                $"Retrieved {reports.Count} draft reports"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting draft reports for organization {OrgShortName}", orgShortName);
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve drafts. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Convert Dictionary<string, object> with JsonElement values to proper objects
    /// This handles ASP.NET Core's JSON deserialization which creates JsonElement objects
    /// </summary>
    private Dictionary<string, object>? ConvertJsonElementDictionary(Dictionary<string, object>? dict)
    {
        if (dict == null) return null;

        var result = new Dictionary<string, object>();
        foreach (var (key, value) in dict)
        {
            result[key] = ConvertJsonElement(value);
        }
        return result;
    }

    /// <summary>
    /// Recursively convert JsonElement to proper .NET types
    /// </summary>
    private object ConvertJsonElement(object value)
    {
        if (value is JsonElement element)
        {
            return element.ValueKind switch
            {
                JsonValueKind.String => element.GetString() ?? string.Empty,
                JsonValueKind.Number => element.TryGetInt64(out var longValue) ? longValue : element.GetDouble(),
                JsonValueKind.True => true,
                JsonValueKind.False => false,
                JsonValueKind.Null => BsonNull.Value,
                JsonValueKind.Array => element.EnumerateArray().Select(e => ConvertJsonElement(e)).ToList(),
                JsonValueKind.Object => element.EnumerateObject().ToDictionary(
                    prop => prop.Name,
                    prop => ConvertJsonElement(prop.Value)),
                _ => value
            };
        }
        return value;
    }
}

/// <summary>
/// Request model for submitting a report
/// </summary>
public class SubmitReportRequest
{
    public string SubmittedBy { get; set; } = string.Empty;
}
