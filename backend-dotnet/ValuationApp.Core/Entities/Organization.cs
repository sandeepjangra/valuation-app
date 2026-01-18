using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Organization entity representing a tenant/organization in the system
/// </summary>
public class Organization
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("shortName")]
    public string ShortName { get; set; } = string.Empty;

    [BsonElement("fullName")]
    public string FullName { get; set; } = string.Empty;

    [BsonElement("reportReferenceInitials")]
    public string? ReportReferenceInitials { get; set; }

    [BsonElement("lastReferenceNumber")]
    public int LastReferenceNumber { get; set; } = 0;

    [BsonElement("isActive")]
    public bool IsActive { get; set; } = true;

    [BsonElement("createdAt")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("updatedAt")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("description")]
    public string? Description { get; set; }

    [BsonElement("contactEmail")]
    public string? ContactEmail { get; set; }

    [BsonElement("contactPhone")]
    public string? ContactPhone { get; set; }
}
