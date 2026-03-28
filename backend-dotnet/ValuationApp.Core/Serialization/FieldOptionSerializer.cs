using MongoDB.Bson;
using MongoDB.Bson.Serialization;
using MongoDB.Bson.Serialization.Serializers;
using ValuationApp.Core.Entities;

namespace ValuationApp.Core.Serialization;

public class FieldOptionSerializer : SerializerBase<FieldOption>
{
    public override FieldOption Deserialize(BsonDeserializationContext context, BsonDeserializationArgs args)
    {
        // Deserialize as BsonDocument first
        var document = BsonDocumentSerializer.Instance.Deserialize(context, args);
        
        var fieldOption = new FieldOption
        {
            Value = document.Contains("value") ? document["value"].AsString : string.Empty,
            Label = document.Contains("label") ? document["label"].AsString : string.Empty,
            IsDefault = document.Contains("isDefault") ? document["isDefault"].AsBoolean : false
        };
        
        return fieldOption;
    }

    public override void Serialize(BsonSerializationContext context, BsonSerializationArgs args, FieldOption value)
    {
        var document = new BsonDocument
        {
            { "value", value.Value },
            { "label", value.Label },
            { "isDefault", value.IsDefault }
        };
        
        BsonDocumentSerializer.Instance.Serialize(context, args, document);
    }
}
