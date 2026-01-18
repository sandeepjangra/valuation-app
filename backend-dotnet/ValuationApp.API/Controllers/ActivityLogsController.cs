using Microsoft.AspNetCore.Mvc;
using ValuationApp.Core.Interfaces;
using ValuationApp.Core.Entities;

namespace ValuationApp.API.Controllers;

[ApiController]
[Route("api/activity-logs")]
public class ActivityLogsController : ControllerBase
{
    private readonly IActivityLoggingService _activityLoggingService;
    private readonly ILogger<ActivityLogsController> _logger;

    public ActivityLogsController(
        IActivityLoggingService activityLoggingService,
        ILogger<ActivityLogsController> logger)
    {
        _activityLoggingService = activityLoggingService;
        _logger = logger;
    }

    /// <summary>
    /// Log a new activity
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<string>> LogActivity([FromBody] LogActivityRequest request)
    {
        try
        {
            // Get IP address and user agent from request
            var ipAddress = HttpContext.Connection.RemoteIpAddress?.ToString();
            var userAgent = HttpContext.Request.Headers["User-Agent"].ToString();

            var activityId = await _activityLoggingService.LogActivityAsync(
                request.UserId,
                request.OrgShortName,
                request.Action,
                request.ActionType,
                request.Description,
                request.EntityType,
                request.EntityId,
                request.Metadata,
                ipAddress,
                userAgent
            );

            return Ok(new { success = true, data = new { id = activityId } });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error logging activity");
            return StatusCode(500, new { success = false, message = "Error logging activity" });
        }
    }

    /// <summary>
    /// Get activities for current user
    /// </summary>
    [HttpGet("user/{userId}")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetUserActivity(
        string userId,
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetUserActivityAsync(userId, limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user activity");
            return StatusCode(500, new { success = false, message = "Error getting user activity" });
        }
    }

    /// <summary>
    /// Get activities for an organization
    /// </summary>
    [HttpGet("org/{orgShortName}")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetOrgActivity(
        string orgShortName,
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetOrgActivityAsync(orgShortName, limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting organization activity");
            return StatusCode(500, new { success = false, message = "Error getting organization activity" });
        }
    }

    /// <summary>
    /// Get all activities (system admin only)
    /// </summary>
    [HttpGet("all")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetAllActivity(
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetAllActivityAsync(limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting all activities");
            return StatusCode(500, new { success = false, message = "Error getting all activities" });
        }
    }

    /// <summary>
    /// Get activities by action type
    /// </summary>
    [HttpGet("type/{actionType}")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetActivitiesByType(
        string actionType,
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetActivitiesByTypeAsync(actionType, limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities by type");
            return StatusCode(500, new { success = false, message = "Error getting activities by type" });
        }
    }

    /// <summary>
    /// Get activities for a specific entity
    /// </summary>
    [HttpGet("entity/{entityType}/{entityId}")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetEntityActivity(
        string entityType,
        string entityId,
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetEntityActivityAsync(entityType, entityId, limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting entity activity");
            return StatusCode(500, new { success = false, message = "Error getting entity activity" });
        }
    }

    /// <summary>
    /// Get activities by date range
    /// </summary>
    [HttpGet("date-range")]
    public async Task<ActionResult<List<ActivityLogEntry>>> GetActivitiesByDateRange(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate,
        [FromQuery] string? orgShortName = null,
        [FromQuery] int limit = 100,
        [FromQuery] int skip = 0)
    {
        try
        {
            var activities = await _activityLoggingService.GetActivitiesByDateRangeAsync(
                startDate, endDate, orgShortName, limit, skip);
            return Ok(new { success = true, data = activities });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities by date range");
            return StatusCode(500, new { success = false, message = "Error getting activities by date range" });
        }
    }

    /// <summary>
    /// Get activity counts by type for analytics
    /// </summary>
    [HttpGet("analytics/counts")]
    public async Task<ActionResult<Dictionary<string, int>>> GetActivityCountsByType(
        [FromQuery] string? orgShortName = null,
        [FromQuery] int days = 30)
    {
        try
        {
            var counts = await _activityLoggingService.GetActivityCountsByTypeAsync(orgShortName, days);
            return Ok(new { success = true, data = counts });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activity counts");
            return StatusCode(500, new { success = false, message = "Error getting activity counts" });
        }
    }
}

/// <summary>
/// Request model for logging an activity
/// </summary>
public class LogActivityRequest
{
    public string UserId { get; set; } = string.Empty;
    public string OrgShortName { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty;
    public string ActionType { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? EntityType { get; set; }
    public string? EntityId { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}
