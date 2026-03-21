using MongoDB.Bson;
using MongoDB.Driver;
using DotNetEnv;

// Load environment variables
var envPath = Path.Combine(Directory.GetCurrentDirectory(), "..", "..", "..", ".env");
if (File.Exists(envPath))
{
    Env.Load(envPath);
    Console.WriteLine("✅ Loaded .env file");
}

var connectionString = Environment.GetEnvironmentVariable("MONGODB_URI");
if (string.IsNullOrEmpty(connectionString))
{
    Console.WriteLine("❌ MONGODB_URI not found in environment");
    return;
}

var client = new MongoClient(connectionString);
var database = client.GetDatabase("valuation_templates");
var collection = database.GetCollection<BsonDocument>("templates");

// Find SBI Land template
var filter = Builders<BsonDocument>.Filter.And(
    Builders<BsonDocument>.Filter.Eq("BankDetails.BankCode", "SBI"),
    Builders<BsonDocument>.Filter.Eq("PropertyType", "Land")
);

var template = await collection.Find(filter).FirstOrDefaultAsync();

if (template != null)
{
    Console.WriteLine($"\n✅ Found template: {template.GetValue("TemplateId", "N/A")}");
    
    // Check timestamp fields
    Console.WriteLine($"\n📅 Timestamp Fields:");
    Console.WriteLine($"  - CreatedAt: {template.GetValue("CreatedAt", "NOT FOUND")} (Type: {template.GetValue("CreatedAt", BsonNull.Value).BsonType})");
    Console.WriteLine($"  - UpdatedAt: {template.GetValue("UpdatedAt", "NOT FOUND")} (Type: {template.GetValue("UpdatedAt", BsonNull.Value).BsonType})");
    
    if (template.Contains("Elements") && template["Elements"].IsBsonArray)
    {
        var elements = template["Elements"].AsBsonArray;
        Console.WriteLine($"\n📊 Total Elements: {elements.Count}");
        
        if (elements.Count > 0)
        {
            var firstElement = elements[0].AsBsonDocument;
            Console.WriteLine($"\n🔍 First Element Keys:");
            foreach (var key in firstElement.Names)
            {
                Console.WriteLine($"  - {key}");
            }
            
            Console.WriteLine($"\n🎯 Discriminator Field Values:");
            Console.WriteLine($"  - $type: {firstElement.GetValue("$type", "NOT FOUND")}");
            Console.WriteLine($"  - Type: {firstElement.GetValue("Type", "NOT FOUND")}");
            Console.WriteLine($"  - _t: {firstElement.GetValue("_t", "NOT FOUND")}");
            
            Console.WriteLine($"\n📄 Full First Element:");
            Console.WriteLine(firstElement.ToJson(new MongoDB.Bson.IO.JsonWriterSettings { Indent = true }));
        }
    }
    else
    {
        Console.WriteLine("\n❌ No Elements array found");
    }
}
else
{
    Console.WriteLine("\n❌ Template not found");
}
