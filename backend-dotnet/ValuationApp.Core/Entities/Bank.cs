using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

[BsonIgnoreExtraElements]
public class Bank
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; } = string.Empty;

    [BsonElement("BankId")]
    public string BankId { get; set; } = string.Empty;

    [BsonElement("BankCode")]
    public string BankCode { get; set; } = string.Empty;

    [BsonElement("BankName")]
    public string BankName { get; set; } = string.Empty;

    [BsonElement("BankShortName")]
    public string BankShortName { get; set; } = string.Empty;

    [BsonElement("BankType")]
    public string BankType { get; set; } = string.Empty;

    [BsonElement("IsActive")]
    public bool IsActive { get; set; } = true;

    [BsonElement("Headquarters")]
    [BsonIgnoreIfNull]
    public HeadquartersInfo? Headquarters { get; set; }

    [BsonElement("TotalBranches")]
    [BsonIgnoreIfNull]
    public int? TotalBranches { get; set; }

    [BsonElement("Branches")]
    public List<BranchEntity> Branches { get; set; } = new();

    [BsonElement("Templates")]
    public List<TemplateReference> Templates { get; set; } = new();

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
