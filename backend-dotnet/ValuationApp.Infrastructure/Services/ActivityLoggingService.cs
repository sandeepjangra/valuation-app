using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;
using Microsoft.Extensions.Logging;

namespace ValuationApp.Infrastructure.Services;

public class ActivityLoggingService : IActivityLoggingService
{
    private readonly MongoDbContext _context;
    private readonly ILogger<ActivityLoggingService> _logger;

    public ActivityLoggingService(MongoDbContext context, ILogger<ActivityLoggingService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<string> LogActivityAsync(
        string userId,
        string orgShortName,
        string action,
        string actionType,
        string description,
        string? entityType = null,
        string? entityId = null,
        Dictionary<string, object>? metadata = null,
        string? ipAddress = null,
        string? userAgent = null)
    {
        try
        {
            var activityLog = new ActivityLogEntry
            {
                UserId = userId,
                OrgShortName = orgShortName,
                Action = action,
                ActionType = actionType,
                Description = description,
                EntityType = entityType,
                EntityId = entityId,
                Metadata = metadata,
                IpAddress = ipAddress,
                UserAgent = userAgent,
                Timestamp = DateTime.UtcNow
            };

            await _context.ActivityLogs.InsertOneAsync(activityLog);
            
            _logger.LogInformation(
                "Activity logged: User={UserId}, Action={Action}, Type={ActionType}, Entity={EntityType}:{EntityId}",
                userId, action, actionType, entityType, entityId
            );

            return activityLog.Id!;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error logging activity for user {UserId}, action {Action}", userId, action);
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetUserActivityAsync(string userId, int limit = 100, int skip = 0)
    {
        try
        {
            return await _context.ActivityLogs
                .Find(log => log.UserId == userId)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activity for user {UserId}", userId);
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetOrgActivityAsync(string orgShortName, int limit = 100, int skip = 0)
    {
        try
        {
            return await _context.ActivityLogs
                .Find(log => log.OrgShortName == orgShortName)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activity for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetAllActivityAsync(int limit = 100, int skip = 0)
    {
        try
        {
            return await _context.ActivityLogs
                .Find(_ => true)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting all activity logs");
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetActivitiesByTypeAsync(string actionType, int limit = 100, int skip = 0)
    {
        try
        {
            return await _context.ActivityLogs
                .Find(log => log.ActionType == actionType)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities by type {ActionType}", actionType);
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetEntityActivityAsync(string entityType, string entityId, int limit = 100, int skip = 0)
    {
        try
        {
            return await _context.ActivityLogs
                .Find(log => log.EntityType == entityType && log.EntityId == entityId)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting entity activity for {EntityType}:{EntityId}", entityType, entityId);
            throw;
        }
    }

    public async Task<List<ActivityLogEntry>> GetActivitiesByDateRangeAsync(
        DateTime startDate,
        DateTime endDate,
        string? orgShortName = null,
        int limit = 100,
        int skip = 0)
    {
        try
        {
            var filterBuilder = Builders<ActivityLogEntry>.Filter;
            var filter = filterBuilder.Gte(log => log.Timestamp, startDate) & 
                        filterBuilder.Lte(log => log.Timestamp, endDate);

            if (!string.IsNullOrEmpty(orgShortName))
            {
                filter &= filterBuilder.Eq(log => log.OrgShortName, orgShortName);
            }

            return await _context.ActivityLogs
                .Find(filter)
                .SortByDescending(log => log.Timestamp)
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activities by date range");
            throw;
        }
    }

    public async Task<Dictionary<string, int>> GetActivityCountsByTypeAsync(string? orgShortName = null, int days = 30)
    {
        try
        {
            var startDate = DateTime.UtcNow.AddDays(-days);
            var filterBuilder = Builders<ActivityLogEntry>.Filter;
            var filter = filterBuilder.Gte(log => log.Timestamp, startDate);

            if (!string.IsNullOrEmpty(orgShortName))
            {
                filter &= filterBuilder.Eq(log => log.OrgShortName, orgShortName);
            }

            var activities = await _context.ActivityLogs
                .Find(filter)
                .ToListAsync();

            return activities
                .GroupBy(log => log.ActionType)
                .ToDictionary(g => g.Key, g => g.Count());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activity counts by type");
            throw;
        }
    }
}
