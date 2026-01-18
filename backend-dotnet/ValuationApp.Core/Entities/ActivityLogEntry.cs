using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Activity log entry for tracking user actions across the system
/// </summary>
[BsonIgnoreExtraElements]
public class ActivityLogEntry
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("user_id")]
    public string UserId { get; set; } = string.Empty;

    [BsonElement("org_short_name")]
    public string OrgShortName { get; set; } = string.Empty;

    [BsonElement("action")]
    public string Action { get; set; } = string.Empty;

    [BsonElement("action_type")]
    public string ActionType { get; set; } = string.Empty;

    [BsonElement("description")]
    public string Description { get; set; } = string.Empty;

    [BsonElement("entity_type")]
    public string? EntityType { get; set; }

    [BsonElement("entity_id")]
    public string? EntityId { get; set; }

    [BsonElement("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }

    [BsonElement("ip_address")]
    public string? IpAddress { get; set; }

    [BsonElement("user_agent")]
    public string? UserAgent { get; set; }

    [BsonElement("timestamp")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    [BsonElement("created_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
