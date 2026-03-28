using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using System.Text.Json.Serialization;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Main template entity in the new C# PascalCase structure
/// Maps to valuation_templates.templates collection
/// </summary>
[BsonIgnoreExtraElements]
public class Template
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("TemplateId")]
    public string TemplateId { get; set; } = string.Empty;

    [BsonElement("TemplateName")]
    public string TemplateName { get; set; } = string.Empty;

    [BsonElement("TemplateDescription")]
    public string? TemplateDescription { get; set; }

    [BsonElement("BankDetails")]
    public BankDetails BankDetails { get; set; } = new();

    [BsonElement("PropertyType")]
    public string PropertyType { get; set; } = string.Empty;

    [BsonElement("Elements")]
    public List<TemplateElement> Elements { get; set; } = new();

    [BsonElement("CalculationRules")]
    public List<CalculationRule> CalculationRules { get; set; } = new();

    [BsonElement("Version")]
    [BsonIgnoreIfNull]
    public string? Version { get; set; }

    [BsonElement("Status")]
    [BsonIgnoreIfNull]
    public string? Status { get; set; }

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

/// <summary>
/// Bank details within a template
/// </summary>
[BsonIgnoreExtraElements]
public class BankDetails
{
    [BsonElement("BankCode")]
    public string BankCode { get; set; } = string.Empty;

    [BsonElement("BankName")]
    public string BankName { get; set; } = string.Empty;
}

/// <summary>
/// Base class for all template elements (polymorphic with $type discriminator)
/// </summary>
[BsonIgnoreExtraElements]
[BsonDiscriminator(RootClass = true, Required = true)]
[BsonKnownTypes(typeof(InputElement), typeof(ContainerElement), typeof(TableElement))]
public abstract class TemplateElement
{
    // This property is for JSON serialization only - MongoDB uses its own discriminator handling
    [BsonIgnore]
    [JsonPropertyName("$type")]
    public abstract string Type { get; }

    [BsonElement("FieldId")]
    public string FieldId { get; set; } = string.Empty;

    [BsonElement("Label")]
    public string Label { get; set; } = string.Empty;

    [BsonElement("DisplayOrder")]
    public int DisplayOrder { get; set; }

    [BsonElement("IsVisible")]
    public bool IsVisible { get; set; } = true;
}

/// <summary>
/// Input field element (text, number, date, dropdown, etc.)
/// </summary>
[BsonIgnoreExtraElements]
[BsonDiscriminator("input")]
public class InputElement : TemplateElement
{
    public override string Type => "input";

    [BsonElement("SpecificType")]
    public string SpecificType { get; set; } = string.Empty; // Text, Number, Date, Dropdown, Currency, etc.

    [BsonElement("IsRequired")]
    public bool IsRequired { get; set; }

    [BsonElement("DefaultValue")]
    [BsonIgnoreIfNull]
    public object? DefaultValue { get; set; }

    [BsonElement("HelpText")]
    [BsonIgnoreIfNull]
    public string? HelpText { get; set; }

    [BsonElement("PlaceholderText")]
    [BsonIgnoreIfNull]
    public string? PlaceholderText { get; set; }

    [BsonElement("IsReadonly")]
    public bool IsReadonly { get; set; }

    [BsonElement("IsCalculated")]
    public bool IsCalculated { get; set; }

    [BsonElement("ValidationRules")]
    [BsonIgnoreIfNull]
    public InputValidationRules? ValidationRules { get; set; }

    [BsonElement("Options")]
    [BsonIgnoreIfNull]
    public List<FieldOption>? Options { get; set; }

    [BsonElement("DependsOn")]
    [BsonIgnoreIfNull]
    public List<string>? DependsOn { get; set; }

    [BsonElement("ConditionalDisplay")]
    [BsonIgnoreIfNull]
    public ConditionalDisplay? ConditionalDisplay { get; set; }
}

/// <summary>
/// Container element (tabs, sections, groups)
/// </summary>
[BsonIgnoreExtraElements]
[BsonDiscriminator("container")]
public class ContainerElement : TemplateElement
{
    public override string Type => "container";

    [BsonElement("Container")] // MongoDB field is "Container", not "ContainerType"
    public string ContainerType { get; set; } = string.Empty; // Tab, Section, Group

    [BsonElement("Children")]
    public List<TemplateElement> Children { get; set; } = new();

    [BsonElement("IsCollapsible")]
    public bool IsCollapsible { get; set; }

    [BsonElement("IsCollapsed")]
    public bool IsCollapsed { get; set; }
}

/// <summary>
/// Table element with columns and rows
/// </summary>
[BsonIgnoreExtraElements]
[BsonDiscriminator("table")]
public class TableElement : TemplateElement
{
    public override string Type => "table";

    [BsonElement("TableType")]
    public string TableType { get; set; } = string.Empty; // Static, Dynamic

    [BsonElement("Columns")]
    public List<TableColumn> Columns { get; set; } = new();

    [BsonElement("Rows")]
    [BsonIgnoreIfNull]
    public List<Dictionary<string, object>>? Rows { get; set; }

    [BsonElement("MinRows")]
    public int MinRows { get; set; } = 1;

    [BsonElement("MaxRows")]
    [BsonIgnoreIfNull]
    public int? MaxRows { get; set; }

    [BsonElement("AllowAddRows")]
    public bool AllowAddRows { get; set; }

    [BsonElement("AllowDeleteRows")]
    public bool AllowDeleteRows { get; set; }
}

/// <summary>
/// Table column definition
/// </summary>
[BsonIgnoreExtraElements]
public class TableColumn
{
    [BsonElement("FieldId")]
    public string FieldId { get; set; } = string.Empty;

    [BsonElement("Label")]
    public string Label { get; set; } = string.Empty;

    [BsonElement("FieldType")]
    public string FieldType { get; set; } = string.Empty; // text, number, date, dropdown

    [BsonElement("Width")]
    [BsonIgnoreIfNull]
    public string? Width { get; set; }

    [BsonElement("IsReadonly")]
    public bool IsReadonly { get; set; }

    [BsonElement("Options")]
    [BsonIgnoreIfNull]
    public List<FieldOption>? Options { get; set; }

    [BsonElement("ValidationRules")]
    [BsonIgnoreIfNull]
    public InputValidationRules? ValidationRules { get; set; }
}

/// <summary>
/// Validation rules for input fields
/// </summary>
[BsonIgnoreExtraElements]
public class InputValidationRules
{
    [BsonElement("Min")]
    [BsonIgnoreIfNull]
    public double? Min { get; set; }

    [BsonElement("Max")]
    [BsonIgnoreIfNull]
    public double? Max { get; set; }

    [BsonElement("MinLength")]
    [BsonIgnoreIfNull]
    public int? MinLength { get; set; }

    [BsonElement("MaxLength")]
    [BsonIgnoreIfNull]
    public int? MaxLength { get; set; }

    [BsonElement("Pattern")]
    [BsonIgnoreIfNull]
    public string? Pattern { get; set; }

    [BsonElement("CustomMessage")]
    [BsonIgnoreIfNull]
    public string? CustomMessage { get; set; }
}

/// <summary>
/// Dropdown/select options
/// </summary>
[BsonIgnoreExtraElements]
public class FieldOption
{
    // No [BsonElement] attributes - using BsonClassMap in Program.cs instead
    public string Value { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public bool IsDefault { get; set; }
}

/// <summary>
/// Conditional display logic
/// </summary>
[BsonIgnoreExtraElements]
public class ConditionalDisplay
{
    [BsonElement("Field")]
    public string Field { get; set; } = string.Empty;

    [BsonElement("Operator")]
    public string Operator { get; set; } = string.Empty; // equals, not_equals, contains, etc.

    [BsonElement("Value")]
    public object? Value { get; set; }
}

/// <summary>
/// Calculation rule (formula)
/// </summary>
[BsonIgnoreExtraElements]
public class CalculationRule
{
    [BsonElement("RuleId")]
    public string RuleId { get; set; } = string.Empty;

    [BsonElement("RuleName")]
    [BsonIgnoreIfNull]
    public string? RuleName { get; set; }

    [BsonElement("Description")]
    [BsonIgnoreIfNull]
    public string? Description { get; set; }

    [BsonElement("Formula")]
    public string Formula { get; set; } = string.Empty;

    [BsonElement("TriggerFieldIds")]
    public List<string> TriggerFieldIds { get; set; } = new();

    [BsonElement("TargetFieldId")]
    public string TargetFieldId { get; set; } = string.Empty;

    [BsonElement("ExecutionOrder")]
    [BsonIgnoreIfNull]
    public int? ExecutionOrder { get; set; }

    [BsonElement("IsActive")]
    public bool IsActive { get; set; } = true;
}
