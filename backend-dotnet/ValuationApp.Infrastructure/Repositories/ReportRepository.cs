using Microsoft.Extensions.Logging;
using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

/// <summary>
/// MongoDB repository for Report operations
/// Reports are stored in organization-specific databases
/// </summary>
public class ReportRepository : IReportRepository
{
    private readonly MongoDbContext _context;
    private readonly ILogger<ReportRepository> _logger;

    public ReportRepository(MongoDbContext context, ILogger<ReportRepository> logger)
    {
        _context = context;
        _logger = logger;
    }

    /// <summary>
    /// Get the reports collection for a specific organization
    /// Each organization has its own database, reports stored in "reports" collection
    /// </summary>
    private IMongoCollection<Report> GetCollection(string orgShortName)
    {
        var database = _context.Client.GetDatabase(orgShortName);
        return database.GetCollection<Report>("reports");
    }

    public async Task<List<Report>> GetAllAsync(string orgShortName, string? status = null, string? bankCode = null, int skip = 0, int limit = 50)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filterBuilder = Builders<Report>.Filter;
            var filter = filterBuilder.Empty;

            if (!string.IsNullOrEmpty(status))
            {
                filter &= filterBuilder.Eq(r => r.Status, status);
            }

            if (!string.IsNullOrEmpty(bankCode))
            {
                filter &= filterBuilder.Eq(r => r.BankCode, bankCode);
            }

            return await collection.Find(filter)
                .Sort(Builders<Report>.Sort.Descending(r => r.CreatedAt))
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<long> GetCountAsync(string orgShortName, string? status = null, string? bankCode = null)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filterBuilder = Builders<Report>.Filter;
            var filter = filterBuilder.Empty;

            if (!string.IsNullOrEmpty(status))
            {
                filter &= filterBuilder.Eq(r => r.Status, status);
            }

            if (!string.IsNullOrEmpty(bankCode))
            {
                filter &= filterBuilder.Eq(r => r.BankCode, bankCode);
            }

            return await collection.CountDocumentsAsync(filter);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error counting reports for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<Report?> GetByIdAsync(string orgShortName, string reportId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.ReportId, reportId);
            return await collection.Find(filter).FirstOrDefaultAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<Report?> GetByReferenceNumberAsync(string orgShortName, string referenceNumber)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.ReferenceNumber, referenceNumber);
            return await collection.Find(filter).FirstOrDefaultAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting report by reference {ReferenceNumber} for organization {OrgShortName}", 
                referenceNumber, orgShortName);
            throw;
        }
    }

    public async Task<string> CreateAsync(string orgShortName, Report report)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            report.CreatedAt = DateTime.UtcNow;
            report.UpdatedAt = DateTime.UtcNow;
            report.OrgShortName = orgShortName;

            await collection.InsertOneAsync(report);
            return report.ReportId;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating report for organization {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateAsync(string orgShortName, string reportId, Report report)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.ReportId, reportId);
            
            report.UpdatedAt = DateTime.UtcNow;
            report.Version++;

            var result = await collection.ReplaceOneAsync(filter, report);
            return result.ModifiedCount > 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> DeleteAsync(string orgShortName, string reportId)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.ReportId, reportId);
            var result = await collection.DeleteOneAsync(filter);
            return result.DeletedCount > 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting report {ReportId} for organization {OrgShortName}", reportId, orgShortName);
            throw;
        }
    }

    public async Task<bool> UpdateStatusAsync(string orgShortName, string reportId, string status)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.ReportId, reportId);
            var update = Builders<Report>.Update
                .Set(r => r.Status, status)
                .Set(r => r.UpdatedAt, DateTime.UtcNow);

            var result = await collection.UpdateOneAsync(filter, update);
            return result.ModifiedCount > 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating status for report {ReportId} in organization {OrgShortName}", 
                reportId, orgShortName);
            throw;
        }
    }

    public async Task<List<Report>> GetByCreatedByAsync(string orgShortName, string userEmail, int skip = 0, int limit = 50)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.CreatedByEmail, userEmail);
            
            return await collection.Find(filter)
                .Sort(Builders<Report>.Sort.Descending(r => r.CreatedAt))
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports created by {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);
            throw;
        }
    }

    public async Task<List<Report>> GetByAssignedToAsync(string orgShortName, string userEmail, int skip = 0, int limit = 50)
    {
        try
        {
            var collection = GetCollection(orgShortName);
            var filter = Builders<Report>.Filter.Eq(r => r.AssignedToEmail, userEmail);
            
            return await collection.Find(filter)
                .Sort(Builders<Report>.Sort.Descending(r => r.CreatedAt))
                .Skip(skip)
                .Limit(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting reports assigned to {UserEmail} in organization {OrgShortName}", 
                userEmail, orgShortName);
            throw;
        }
    }
}
