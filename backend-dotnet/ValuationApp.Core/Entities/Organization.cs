using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

[BsonIgnoreExtraElements]
public class Organization
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; } = string.Empty;

    [BsonElement("OrganizationId")]
    public string OrganizationId { get; set; } = string.Empty;

    [BsonElement("ShortName")]
    public string ShortName { get; set; } = string.Empty;

    [BsonElement("FullName")]
    public string FullName { get; set; } = string.Empty;

    [BsonElement("Description")]
    public string? Description { get; set; }

    [BsonElement("ReportReferenceInitials")]
    public string? ReportReferenceInitials { get; set; }

    [BsonElement("LastReferenceNumber")]
    public int LastReferenceNumber { get; set; }

    [BsonElement("ContactEmail")]
    public string? ContactEmail { get; set; }

    [BsonElement("ContactPhone")]
    public string? ContactPhone { get; set; }

    [BsonElement("IsActive")]
    public bool IsActive { get; set; } = true;

    [BsonElement("CreatedAt")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? CreatedAt { get; set; }

    [BsonElement("UpdatedAt")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? UpdatedAt { get; set; }

    [BsonElement("MigratedFrom")]
    [BsonIgnoreIfNull]
    public string? MigratedFrom { get; set; }

    [BsonElement("MigrationDate")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? MigrationDate { get; set; }

    [BsonElement("MigrationScript")]
    [BsonIgnoreIfNull]
    public string? MigrationScript { get; set; }
}
