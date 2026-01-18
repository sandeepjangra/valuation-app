using Microsoft.Extensions.Logging;
using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

/// <summary>
/// MongoDB repository for UserProfile operations
/// UserProfiles are stored in organization-specific databases
/// </summary>
public class UserProfileRepository : IUserProfileRepository
{
    private readonly MongoDbContext _context;
    private readonly ILogger<UserProfileRepository> _logger;

    public UserProfileRepository(MongoDbContext context, ILogger<UserProfileRepository> logger)
    {
        _context = context;
        _logger = logger;
    }

    /// <summary>
    /// Get the user_profiles collection for a specific organization
    /// </summary>
    private IMongoCollection<UserProfile> GetCollection(string orgShortName)
    {
        var database = _context.Client.GetDatabase(orgShortName);
        return database.GetCollection<UserProfile>("user_profiles");
    }

    public async Task<UserProfile?> GetByUserIdAsync(string orgShortName, string userId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            return await collection.Find(filter).FirstOrDefaultAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user profile for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<string> CreateAsync(string orgShortName, UserProfile profile)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            profile.CreatedAt = DateTime.UtcNow;
            profile.UpdatedAt = DateTime.UtcNow;
            profile.OrgShortName = orgShortName;

            await collection.InsertOneAsync(profile);
            return profile.UserId;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user profile for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateAsync(string orgShortName, UserProfile profile)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, profile.UserId);
            
            profile.UpdatedAt = DateTime.UtcNow;

            var result = await collection.ReplaceOneAsync(filter, profile);
            return result.ModifiedCount > 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user profile for {UserId} in organization {OrgShortName}", 
                profile.UserId, orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateLastLoginAsync(string orgShortName, string userId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            var update = Builders<UserProfile>.Update
                .Set(p => p.LastLogin, DateTime.UtcNow)
                .Set(p => p.LastActivity, DateTime.UtcNow)
                .Inc(p => p.LoginCount, 1)
                .Set(p => p.UpdatedAt, DateTime.UtcNow);

            var result = await collection.UpdateOneAsync(filter, update);
            return result.ModifiedCount > 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating last login for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<bool> LogActivityAsync(string orgShortName, string userId, ActivityLog log)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            var update = Builders<UserProfile>.Update
                .Push(p => p.ActivityLogs, log)
                .Set(p => p.LastActivity, DateTime.UtcNow)
                .Set(p => p.UpdatedAt, DateTime.UtcNow);

            var result = await collection.UpdateOneAsync(filter, update, new UpdateOptions { IsUpsert = true });
            return result.ModifiedCount > 0 || result.UpsertedId != null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error logging activity for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<List<ActivityLog>> GetActivityLogsAsync(string orgShortName, string userId, int limit = 50)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            var profile = await collection.Find(filter).FirstOrDefaultAsync();

            if (profile?.ActivityLogs == null)
            {
                return new List<ActivityLog>();
            }

            return profile.ActivityLogs
                .OrderByDescending(a => a.Timestamp)
                .Take(limit)
                .ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting activity logs for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<bool> IncrementReportsCreatedAsync(string orgShortName, string userId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            var update = Builders<UserProfile>.Update
                .Inc(p => p.ReportsCreated, 1)
                .Set(p => p.UpdatedAt, DateTime.UtcNow);

            var result = await collection.UpdateOneAsync(filter, update, new UpdateOptions { IsUpsert = true });
            return result.ModifiedCount > 0 || result.UpsertedId != null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error incrementing reports created for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }

    public async Task<bool> IncrementReportsSubmittedAsync(string orgShortName, string userId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<UserProfile>.Filter.Eq(p => p.UserId, userId);
            var update = Builders<UserProfile>.Update
                .Inc(p => p.ReportsSubmitted, 1)
                .Set(p => p.UpdatedAt, DateTime.UtcNow);

            var result = await collection.UpdateOneAsync(filter, update, new UpdateOptions { IsUpsert = true });
            return result.ModifiedCount > 0 || result.UpsertedId != null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error incrementing reports submitted for {UserId} in organization {OrgShortName}", 
                userId, orgShortName);
            throw;
        }
    }
}
