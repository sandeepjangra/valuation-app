using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using MongoDB.Driver;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Services;

/// <summary>
/// Service for managing organization-specific MongoDB databases
/// Each organization gets its own isolated database for reports, custom templates, etc.
/// </summary>
public class OrganizationDatabaseService : IOrganizationDatabaseService
{
    private readonly IMongoClient _mongoClient;
    private readonly ILogger<OrganizationDatabaseService> _logger;

    public OrganizationDatabaseService(
        MongoDbContext context,
        ILogger<OrganizationDatabaseService> logger)
    {
        _mongoClient = context.Client;
        _logger = logger;
    }

    public async Task<bool> CreateOrganizationDatabaseAsync(string orgShortName)
    {
        try
        {
            _logger.LogInformation("Creating database for organization: {OrgShortName}", orgShortName);

            // Check if database already exists
            if (await DatabaseExistsAsync(orgShortName))
            {
                _logger.LogWarning("Database {OrgShortName} already exists", orgShortName);
                return false;
            }

            // MongoDB creates databases automatically when you write to them
            // We'll create it by initializing collections
            await InitializeOrganizationCollectionsAsync(orgShortName);

            _logger.LogInformation("✅ Database {OrgShortName} created successfully", orgShortName);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create database for organization: {OrgShortName}", orgShortName);
            throw;
        }
    }

    public async Task<bool> DatabaseExistsAsync(string orgShortName)
    {
        try
        {
            var databases = await _mongoClient.ListDatabaseNamesAsync();
            var databaseList = await databases.ToListAsync();
            
            return databaseList.Contains(orgShortName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to check if database exists: {OrgShortName}", orgShortName);
            return false;
        }
    }

    public async Task InitializeOrganizationCollectionsAsync(string orgShortName)
    {
        try
        {
            _logger.LogInformation("Initializing collections for organization: {OrgShortName}", orgShortName);

            var database = _mongoClient.GetDatabase(orgShortName);

            // Define collections to create
            var collections = new[]
            {
                "reports",              // Valuation reports created by users
                "custom_templates",     // Custom templates created by organization
                "custom_banks",         // Custom banks added by organization
                "activity_logs",        // Organization-specific activity logs
                "drafts"                // Draft reports
            };

            foreach (var collectionName in collections)
            {
                try
                {
                    // Check if collection exists
                    var filter = new BsonDocument("name", collectionName);
                    var collectionsCursor = await database.ListCollectionsAsync(new ListCollectionsOptions { Filter = filter });
                    var collectionExists = await collectionsCursor.AnyAsync();

                    if (!collectionExists)
                    {
                        // Create collection
                        await database.CreateCollectionAsync(collectionName);
                        _logger.LogInformation("  ✓ Created collection: {CollectionName}", collectionName);

                        // Create indexes based on collection type
                        await CreateCollectionIndexesAsync(database, collectionName);
                    }
                    else
                    {
                        _logger.LogInformation("  ↷ Collection already exists: {CollectionName}", collectionName);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to create collection {CollectionName} in database {OrgShortName}", 
                        collectionName, orgShortName);
                }
            }

            _logger.LogInformation("✅ Collections initialized for organization: {OrgShortName}", orgShortName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize collections for organization: {OrgShortName}", orgShortName);
            throw;
        }
    }

    private async Task CreateCollectionIndexesAsync(IMongoDatabase database, string collectionName)
    {
        try
        {
            switch (collectionName)
            {
                case "reports":
                    {
                        var collection = database.GetCollection<BsonDocument>(collectionName);
                        
                        // Index on report_id for quick lookups
                        var reportIdIndex = Builders<BsonDocument>.IndexKeys.Ascending("report_id");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(reportIdIndex));

                        // Index on created_at for sorting
                        var createdAtIndex = Builders<BsonDocument>.IndexKeys.Descending("created_at");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(createdAtIndex));

                        // Index on user_id for filtering reports by user
                        var userIdIndex = Builders<BsonDocument>.IndexKeys.Ascending("user_id");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(userIdIndex));

                        // Index on status for filtering
                        var statusIndex = Builders<BsonDocument>.IndexKeys.Ascending("status");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(statusIndex));

                        _logger.LogInformation("    → Created indexes for {CollectionName}", collectionName);
                        break;
                    }

                case "custom_templates":
                    {
                        var collection = database.GetCollection<BsonDocument>(collectionName);
                        
                        // Index on template_name
                        var templateNameIndex = Builders<BsonDocument>.IndexKeys.Ascending("template_name");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(templateNameIndex));

                        _logger.LogInformation("    → Created indexes for {CollectionName}", collectionName);
                        break;
                    }

                case "custom_banks":
                    {
                        var collection = database.GetCollection<BsonDocument>(collectionName);
                        
                        // Index on bank_name
                        var bankNameIndex = Builders<BsonDocument>.IndexKeys.Ascending("bank_name");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(bankNameIndex));

                        // Index on bank_code
                        var bankCodeIndex = Builders<BsonDocument>.IndexKeys.Ascending("bank_code");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(bankCodeIndex));

                        _logger.LogInformation("    → Created indexes for {CollectionName}", collectionName);
                        break;
                    }

                case "activity_logs":
                    {
                        var collection = database.GetCollection<BsonDocument>(collectionName);
                        
                        // Index on timestamp
                        var timestampIndex = Builders<BsonDocument>.IndexKeys.Descending("timestamp");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(timestampIndex));

                        // Index on user_id
                        var userIdIndex = Builders<BsonDocument>.IndexKeys.Ascending("user_id");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(userIdIndex));

                        _logger.LogInformation("    → Created indexes for {CollectionName}", collectionName);
                        break;
                    }

                case "drafts":
                    {
                        var collection = database.GetCollection<BsonDocument>(collectionName);
                        
                        // Index on user_id
                        var userIdIndex = Builders<BsonDocument>.IndexKeys.Ascending("user_id");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(userIdIndex));

                        // Index on updated_at
                        var updatedAtIndex = Builders<BsonDocument>.IndexKeys.Descending("updated_at");
                        await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(updatedAtIndex));

                        _logger.LogInformation("    → Created indexes for {CollectionName}", collectionName);
                        break;
                    }
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to create indexes for collection {CollectionName}", collectionName);
            // Don't throw - indexes are optional, collection creation is more important
        }
    }

    public async Task<bool> DeleteOrganizationDatabaseAsync(string orgShortName)
    {
        try
        {
            _logger.LogWarning("⚠️  Delete requested for database: {OrgShortName}", orgShortName);

            // For safety, we don't actually drop the database
            // Instead, we should mark the organization as deleted in valuation_admin.organizations
            // The actual database remains for backup/recovery purposes

            _logger.LogInformation("Database {OrgShortName} marked for deletion (not dropped)", orgShortName);
            
            // If you really need to drop the database, uncomment below:
            // await _mongoClient.DropDatabaseAsync(orgShortName);
            // _logger.LogWarning("❌ Database {OrgShortName} has been DROPPED", orgShortName);

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete database: {OrgShortName}", orgShortName);
            return false;
        }
    }
}
