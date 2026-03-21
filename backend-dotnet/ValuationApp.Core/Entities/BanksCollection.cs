using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Root collection wrapper for banks in the new C# structure
/// Maps to valuation_templates.banks collection (single document with Banks array)
/// </summary>
[BsonIgnoreExtraElements]
public class BanksCollection
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("CollectionName")]
    public string CollectionName { get; set; } = "Banks";

    [BsonElement("Description")]
    public string? Description { get; set; }

    [BsonElement("Version")]
    public string Version { get; set; } = "5.0";

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

    [BsonElement("Banks")]
    public List<BankEntity> Banks { get; set; } = new();
}

/// <summary>
/// Individual bank entity in the new C# PascalCase structure
/// </summary>
[BsonIgnoreExtraElements]
public class BankEntity
{
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
}

/// <summary>
/// Headquarters information with PascalCase properties
/// </summary>
[BsonIgnoreExtraElements]
public class HeadquartersInfo
{
    [BsonElement("City")]
    public string City { get; set; } = string.Empty;

    [BsonElement("State")]
    public string State { get; set; } = string.Empty;

    [BsonElement("Pincode")]
    public string Pincode { get; set; } = string.Empty;
}

/// <summary>
/// Branch entity with PascalCase properties
/// </summary>
[BsonIgnoreExtraElements]
public class BranchEntity
{
    [BsonElement("BranchId")]
    public string BranchId { get; set; } = string.Empty;

    [BsonElement("BranchCode")]
    public string BranchCode { get; set; } = string.Empty;

    [BsonElement("BranchName")]
    public string BranchName { get; set; } = string.Empty;

    [BsonElement("BranchAddress")]
    [BsonIgnoreIfNull]
    public BranchAddressInfo? BranchAddress { get; set; }

    [BsonElement("IfscCode")]
    public string IfscCode { get; set; } = string.Empty;

    [BsonElement("ContactDetails")]
    [BsonIgnoreIfNull]
    public ContactInfo? ContactDetails { get; set; }

    [BsonElement("IsActive")]
    public bool IsActive { get; set; } = true;

    [BsonElement("CreatedAt")]
    [BsonIgnoreIfNull]
    public string? CreatedAt { get; set; }

    [BsonElement("UpdatedAt")]
    [BsonIgnoreIfNull]
    public string? UpdatedAt { get; set; }
}

/// <summary>
/// Branch address with PascalCase properties
/// </summary>
[BsonIgnoreExtraElements]
public class BranchAddressInfo
{
    [BsonElement("Street")]
    public string? Street { get; set; }

    [BsonElement("City")]
    public string City { get; set; } = string.Empty;

    [BsonElement("State")]
    public string State { get; set; } = string.Empty;

    [BsonElement("Pincode")]
    public string Pincode { get; set; } = string.Empty;

    [BsonElement("Country")]
    public string? Country { get; set; }
}

/// <summary>
/// Contact information with PascalCase properties
/// </summary>
[BsonIgnoreExtraElements]
public class ContactInfo
{
    [BsonElement("Phone")]
    public string Phone { get; set; } = string.Empty;

    [BsonElement("Email")]
    public string Email { get; set; } = string.Empty;
}

/// <summary>
/// Template reference in bank entity with PascalCase properties
/// </summary>
[BsonIgnoreExtraElements]
public class TemplateReference
{
    [BsonElement("TemplateId")]
    public string TemplateId { get; set; } = string.Empty;

    [BsonElement("TemplateCode")]
    public string? TemplateCode { get; set; }

    [BsonElement("TemplateName")]
    public string? TemplateName { get; set; }

    [BsonElement("TemplateType")]
    public string? TemplateType { get; set; }

    [BsonElement("PropertyType")]
    public string PropertyType { get; set; } = string.Empty;

    [BsonElement("Description")]
    public string? Description { get; set; }

    [BsonElement("Version")]
    public string? Version { get; set; }

    [BsonElement("IsActive")]
    public bool IsActive { get; set; } = true;

    [BsonElement("CollectionRef")]
    [BsonIgnoreIfNull]
    public string? CollectionRef { get; set; }

    [BsonElement("CommonFieldsCollectionRef")]
    [BsonIgnoreIfNull]
    public string? CommonFieldsCollectionRef { get; set; }
}
