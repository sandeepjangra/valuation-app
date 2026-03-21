using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Root collection wrapper for organizations in the new C# structure
/// Maps to valuation_templates.organizations collection (single document with Organizations array)
/// </summary>
[BsonIgnoreExtraElements]
public class OrganizationsCollection
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("CollectionName")]
    public string CollectionName { get; set; } = "Organizations";

    [BsonElement("Description")]
    public string? Description { get; set; }

    [BsonElement("Version")]
    public string Version { get; set; } = "2.0";

    [BsonElement("MigrationDate")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? MigrationDate { get; set; }

    [BsonElement("CreatedAt")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? CreatedAt { get; set; }

    [BsonElement("UpdatedAt")]
    [BsonIgnoreIfNull]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? UpdatedAt { get; set; }

    [BsonElement("Organizations")]
    public List<OrganizationEntity> Organizations { get; set; } = new();
}

/// <summary>
/// Individual organization entity in the new C# PascalCase structure
/// </summary>
[BsonIgnoreExtraElements]
public class OrganizationEntity
{
    [BsonElement("OrganizationId")]
    public string OrganizationId { get; set; } = string.Empty;

    [BsonElement("ShortName")]
    public string ShortName { get; set; } = string.Empty;

    [BsonElement("FullName")]
    public string FullName { get; set; } = string.Empty;

    [BsonElement("Description")]
    public string? Description { get; set; }

    [BsonElement("ReportReferenceInitials")]
    public string ReportReferenceInitials { get; set; } = string.Empty;

    [BsonElement("LastReferenceNumber")]
    public int LastReferenceNumber { get; set; } = 0;

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
}
