using MongoDB.Driver;
using MongoDB.Bson;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

public class TemplateRepository : ITemplateRepository
{
    private readonly IMongoDatabase _sharedResourcesDb;

    public TemplateRepository(MongoDbContext context)
    {
        // Use shared_resources database for templates
        _sharedResourcesDb = context.Client.GetDatabase("shared_resources");
    }

    public async Task<object?> GetTemplateStructureAsync(string collectionName)
    {
        var collection = _sharedResourcesDb.GetCollection<BsonDocument>(collectionName);
        var document = await collection.Find(_ => true).FirstOrDefaultAsync();
        
        if (document == null)
            return null;

        // Convert BsonDocument to JSON string first, then deserialize with Newtonsoft.Json
        // This avoids the nested array issue with BSON serialization
        var json = document.ToJson(new MongoDB.Bson.IO.JsonWriterSettings { OutputMode = MongoDB.Bson.IO.JsonOutputMode.RelaxedExtendedJson });
        return Newtonsoft.Json.JsonConvert.DeserializeObject(json);
    }

    public async Task<object?> GetCommonFieldsAsync()
    {
        var collection = _sharedResourcesDb.GetCollection<BsonDocument>("common_form_fields");
        var document = await collection.Find(_ => true).FirstOrDefaultAsync();
        
        if (document == null)
            return null;

        var json = document.ToJson(new MongoDB.Bson.IO.JsonWriterSettings { OutputMode = MongoDB.Bson.IO.JsonOutputMode.RelaxedExtendedJson });
        return Newtonsoft.Json.JsonConvert.DeserializeObject(json);
    }

    public async Task<List<object>> GetDocumentTypesAsync(string bankCode, string propertyType)
    {
        var collection = _sharedResourcesDb.GetCollection<BsonDocument>("document_types");
        
        // Filter by bank code and property type
        // Document types have applicableBanks (array) and applicablePropertyTypes (array)
        var filter = Builders<BsonDocument>.Filter.And(
            Builders<BsonDocument>.Filter.Eq("isActive", true),
            Builders<BsonDocument>.Filter.Or(
                Builders<BsonDocument>.Filter.AnyEq("applicableBanks", bankCode),
                Builders<BsonDocument>.Filter.AnyEq("applicableBanks", "*")
            ),
            Builders<BsonDocument>.Filter.Or(
                Builders<BsonDocument>.Filter.AnyEq("applicablePropertyTypes", propertyType),
                Builders<BsonDocument>.Filter.AnyEq("applicablePropertyTypes", propertyType.ToUpper()),
                Builders<BsonDocument>.Filter.AnyEq("applicablePropertyTypes", 
                    char.ToUpper(propertyType[0]) + propertyType.Substring(1).ToLower())
            )
        );

        var documents = await collection.Find(filter)
            .Sort(Builders<BsonDocument>.Sort.Ascending("sortOrder"))
            .ToListAsync();
        
        return documents.Select(doc => {
            var json = doc.ToJson(new MongoDB.Bson.IO.JsonWriterSettings { OutputMode = MongoDB.Bson.IO.JsonOutputMode.RelaxedExtendedJson });
            return Newtonsoft.Json.JsonConvert.DeserializeObject(json);
        }).ToList()!;
    }
}
