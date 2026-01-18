using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

public class Bank
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; } = string.Empty;

    [BsonElement("bankId")]
    public string BankId { get; set; } = string.Empty;

    [BsonElement("bankCode")]
    public string BankCode { get; set; } = string.Empty;

    [BsonElement("bankName")]
    public string BankName { get; set; } = string.Empty;

    [BsonElement("bankShortName")]
    public string BankShortName { get; set; } = string.Empty;

    [BsonElement("bankType")]
    public string BankType { get; set; } = string.Empty;

    [BsonElement("isActive")]
    public bool IsActive { get; set; }

    [BsonElement("headquarters")]
    [BsonIgnoreIfNull]
    public Headquarters? Headquarters { get; set; }

    [BsonElement("totalBranches")]
    [BsonIgnoreIfNull]
    public int? TotalBranches { get; set; }

    [BsonElement("bankBranches")]
    [BsonIgnoreIfNull]
    public List<BankBranch>? BankBranches { get; set; }

    [BsonElement("templates")]
    [BsonIgnoreIfNull]
    public List<BankTemplate>? Templates { get; set; }

    [BsonElement("createdAt")]
    [BsonIgnoreIfNull]
    public object? CreatedAt { get; set; }

    [BsonElement("updatedAt")]
    [BsonIgnoreIfNull]
    public object? UpdatedAt { get; set; }

    [BsonElement("migratedAt")]
    [BsonIgnoreIfNull]
    public object? MigratedAt { get; set; }

    [BsonElement("migrationSource")]
    [BsonIgnoreIfNull]
    public string? MigrationSource { get; set; }
}

public class Headquarters
{
    [BsonElement("city")]
    public string City { get; set; } = string.Empty;

    [BsonElement("state")]
    public string State { get; set; } = string.Empty;

    [BsonElement("pincode")]
    public string Pincode { get; set; } = string.Empty;
}

public class BankBranch
{
    [BsonElement("branchId")]
    public string BranchId { get; set; } = string.Empty;

    [BsonElement("branchCode")]
    public string BranchCode { get; set; } = string.Empty;

    [BsonElement("branchName")]
    public string BranchName { get; set; } = string.Empty;

    [BsonElement("branchAddress")]
    [BsonIgnoreIfNull]
    public BranchAddress? BranchAddress { get; set; }

    [BsonElement("ifscCode")]
    public string IfscCode { get; set; } = string.Empty;

    [BsonElement("contactDetails")]
    [BsonIgnoreIfNull]
    public ContactDetails? ContactDetails { get; set; }

    [BsonElement("isActive")]
    public bool IsActive { get; set; }

    [BsonElement("createdAt")]
    [BsonIgnoreIfNull]
    public object? CreatedAt { get; set; }

    [BsonElement("updatedAt")]
    [BsonIgnoreIfNull]
    public object? UpdatedAt { get; set; }
}

public class BranchAddress
{
    [BsonElement("street")]
    public string Street { get; set; } = string.Empty;

    [BsonElement("city")]
    public string City { get; set; } = string.Empty;

    [BsonElement("state")]
    public string State { get; set; } = string.Empty;

    [BsonElement("pincode")]
    public string Pincode { get; set; } = string.Empty;

    [BsonElement("country")]
    public string Country { get; set; } = string.Empty;
}

public class ContactDetails
{
    [BsonElement("phone")]
    public string Phone { get; set; } = string.Empty;

    [BsonElement("email")]
    public string Email { get; set; } = string.Empty;
}

public class BankTemplate
{
    [BsonElement("templateId")]
    public string TemplateId { get; set; } = string.Empty;

    [BsonElement("templateCode")]
    public string TemplateCode { get; set; } = string.Empty;

    [BsonElement("templateName")]
    public string TemplateName { get; set; } = string.Empty;

    [BsonElement("templateType")]
    public string TemplateType { get; set; } = string.Empty;

    [BsonElement("propertyType")]
    public string PropertyType { get; set; } = string.Empty;

    [BsonElement("description")]
    public string Description { get; set; } = string.Empty;

    [BsonElement("version")]
    public string Version { get; set; } = string.Empty;

    [BsonElement("isActive")]
    public bool IsActive { get; set; }

    [BsonElement("collectionRef")]
    [BsonIgnoreIfNull]
    public string? CollectionRef { get; set; }

    [BsonElement("commonFieldsCollectionRef")]
    [BsonIgnoreIfNull]
    public string? CommonFieldsCollectionRef { get; set; }

    [BsonElement("fields")]
    [BsonIgnoreIfNull]
    public List<string>? Fields { get; set; }

    [BsonElement("validationRules")]
    [BsonIgnoreIfNull]
    public ValidationRules? ValidationRules { get; set; }

    [BsonElement("allowCustomFields")]
    [BsonIgnoreIfNull]
    public bool? AllowCustomFields { get; set; }

    [BsonElement("maxCustomFields")]
    [BsonIgnoreIfNull]
    public int? MaxCustomFields { get; set; }

    [BsonElement("createdAt")]
    [BsonIgnoreIfNull]
    public object? CreatedAt { get; set; }

    [BsonElement("updatedAt")]
    [BsonIgnoreIfNull]
    public object? UpdatedAt { get; set; }
}

public class ValidationRules
{
    [BsonElement("required_fields")]
    [BsonIgnoreIfNull]
    public List<string>? RequiredFields { get; set; }

    [BsonElement("minimum_documents")]
    [BsonIgnoreIfNull]
    public int? MinimumDocuments { get; set; }
}
