using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Interfaces;

public interface IActivityLoggingService
{
    /// <summary>
    /// Log a user activity
    /// </summary>
    Task<string> LogActivityAsync(
        string userId,
        string orgShortName,
        string action,
        string actionType,
        string description,
        string? entityType = null,
        string? entityId = null,
        Dictionary<string, object>? metadata = null,
        string? ipAddress = null,
        string? userAgent = null
    );

    /// <summary>
    /// Get activities for a specific user
    /// </summary>
    Task<List<ActivityLogEntry>> GetUserActivityAsync(string userId, int limit = 100, int skip = 0);

    /// <summary>
    /// Get activities for a specific organization
    /// </summary>
    Task<List<ActivityLogEntry>> GetOrgActivityAsync(string orgShortName, int limit = 100, int skip = 0);

    /// <summary>
    /// Get all activities (system admin only)
    /// </summary>
    Task<List<ActivityLogEntry>> GetAllActivityAsync(int limit = 100, int skip = 0);

    /// <summary>
    /// Get activities by action type
    /// </summary>
    Task<List<ActivityLogEntry>> GetActivitiesByTypeAsync(string actionType, int limit = 100, int skip = 0);

    /// <summary>
    /// Get activities by entity (e.g., all activities on a specific report)
    /// </summary>
    Task<List<ActivityLogEntry>> GetEntityActivityAsync(string entityType, string entityId, int limit = 100, int skip = 0);

    /// <summary>
    /// Get activities within date range
    /// </summary>
    Task<List<ActivityLogEntry>> GetActivitiesByDateRangeAsync(
        DateTime startDate,
        DateTime endDate,
        string? orgShortName = null,
        int limit = 100,
        int skip = 0
    );

    /// <summary>
    /// Get activity count by action type for analytics
    /// </summary>
    Task<Dictionary<string, int>> GetActivityCountsByTypeAsync(string? orgShortName = null, int days = 30);
}
