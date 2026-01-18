using MongoDB.Driver;
using ValuationApp.Core.Entities;

namespace ValuationApp.Infrastructure.Data;

/// <summary>
/// MongoDB context for database operations
/// </summary>
public class MongoDbContext
{
    private readonly IMongoClient _client;
    private readonly IMongoDatabase _adminDatabase;
    private readonly IMongoDatabase _reportsDatabase;

    public MongoDbContext(MongoDbSettings settings)
    {
        _client = new MongoClient(settings.ConnectionString);
        _adminDatabase = _client.GetDatabase(settings.AdminDatabaseName);
        _reportsDatabase = _client.GetDatabase(settings.ReportsDatabaseName);
    }

    /// <summary>
    /// Get MongoDB client for accessing other databases
    /// </summary>
    public IMongoClient Client => _client;

    /// <summary>
    /// Get admin database (contains users, organizations, etc.)
    /// </summary>
    public IMongoDatabase AdminDatabase => _adminDatabase;

    /// <summary>
    /// Get reports database (contains valuation reports)
    /// </summary>
    public IMongoDatabase ReportsDatabase => _reportsDatabase;

    /// <summary>
    /// Organizations collection
    /// </summary>
    public IMongoCollection<Organization> Organizations => 
        _adminDatabase.GetCollection<Organization>("organizations");

    /// <summary>
    /// Activity logs collection
    /// </summary>
    public IMongoCollection<ActivityLogEntry> ActivityLogs => 
        _adminDatabase.GetCollection<ActivityLogEntry>("activity_logs");

    /// <summary>
    /// Permission templates collection
    /// </summary>
    public IMongoCollection<PermissionTemplate> PermissionTemplates => 
        _adminDatabase.GetCollection<PermissionTemplate>("permissions_templates");

    /// <summary>
    /// Get a collection from admin database
    /// </summary>
    public IMongoCollection<T> GetAdminCollection<T>(string collectionName)
    {
        return _adminDatabase.GetCollection<T>(collectionName);
    }

    /// <summary>
    /// Get a collection from reports database
    /// </summary>
    public IMongoCollection<T> GetReportsCollection<T>(string collectionName)
    {
        return _reportsDatabase.GetCollection<T>(collectionName);
    }
}
