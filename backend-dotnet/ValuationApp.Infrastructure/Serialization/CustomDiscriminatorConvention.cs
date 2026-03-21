using MongoDB.Bson;
using MongoDB.Bson.IO;
using MongoDB.Bson.Serialization;
using MongoDB.Bson.Serialization.Conventions;

namespace ValuationApp.Infrastructure.Serialization;

/// <summary>
/// Custom discriminator convention that uses "$type" field instead of default "_t"
/// </summary>
public class CustomDiscriminatorConvention : IDiscriminatorConvention
{
    private readonly string _elementName;

    public CustomDiscriminatorConvention(string elementName)
    {
        _elementName = elementName;
    }

    public string ElementName => _elementName;

    public Type GetActualType(IBsonReader bsonReader, Type nominalType)
    {
        var bookmark = bsonReader.GetBookmark();
        bsonReader.ReadStartDocument();

        Type actualType = nominalType;

        if (bsonReader.FindElement(_elementName))
        {
            var discriminatorValue = BsonValue.Create(bsonReader.ReadString());
            actualType = BsonSerializer.LookupActualType(nominalType, discriminatorValue);
        }

        bsonReader.ReturnToBookmark(bookmark);
        return actualType;
    }

    public BsonValue GetDiscriminator(Type nominalType, Type actualType)
    {
        if (nominalType == actualType)
        {
            return null!;
        }

        // Get the discriminator value from the BsonDiscriminator attribute
        var classMap = BsonClassMap.LookupClassMap(actualType);
        return classMap.Discriminator ?? actualType.Name;
    }
}
