using System.Text.Json.Serialization;

namespace ValuationApp.Core.DTOs;

/// <summary>
/// Main DTO for valuation templates - represents the API contract
/// </summary>
public class ValuationTemplate
{
    public required string TemplateId { get; set; }
    public required string TemplateName { get; set; }
    public string TemplateDescription { get; set; } = string.Empty;
    public required BankDto BankDetails { get; set; }
    public PropertyTypeDto PropertyType { get; set; }

    // The top level can be a mix of Fields, Tabs, or Groups
    public List<BaseField> Elements { get; set; } = new();

    // The logic engine (The "Brain")
    public List<CalculationRule> CalculationRules { get; set; } = new();
    
    // Additional metadata
    public string? Version { get; set; }
    public string? Status { get; set; }
    public bool IsActive { get; set; } = true;
    public DateTime? CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}

/// <summary>
/// Base class for all template fields with polymorphic JSON serialization
/// </summary>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "$type")]
[JsonDerivedType(typeof(InputField), "input")]
[JsonDerivedType(typeof(TableField), "table")]
[JsonDerivedType(typeof(ContainerField), "container")]
[JsonDerivedType(typeof(AttachmentField), "attachment")]
public abstract class BaseField
{
    public required string FieldId { get; set; }
    public required string Label { get; set; }
    public int DisplayOrder { get; set; }
    public abstract FieldTypeDto FieldType { get; }
    public bool IsVisible { get; set; } = true;

    // Logic: If null, it's always visible. If present, evaluate it.
    public VisibilityRule? Visibility { get; set; }
}

/// <summary>
/// Simple Inputs (Text, Number, Date, etc.)
/// </summary>
public class InputField : BaseField
{
    // The specific type is passed via constructor or property
    public FieldTypeDto SpecificType { get; set; }
    public override FieldTypeDto FieldType => SpecificType;
    public string? DefaultValue { get; set; }
    public bool IsRequired { get; set; }
    public bool IsReadonly { get; set; }
    public string? HelpText { get; set; }
    public string? PlaceholderText { get; set; }
    public List<string>? Options { get; set; } // For Dropdowns
    public InputValidationRulesDto? ValidationRules { get; set; }
}

/// <summary>
/// Containers (Tabs, Groups, Sections)
/// </summary>
public class ContainerField : BaseField
{
    public ContainerTypeDto Container { get; set; }
    
    // Logic: Map ContainerType back to FieldType
    public override FieldTypeDto FieldType => Container switch 
    {
        ContainerTypeDto.Tab => FieldTypeDto.Tab,
        ContainerTypeDto.Group => FieldTypeDto.Group,
        _ => FieldTypeDto.Section
    };
    
    // This is the recursive part: a container holds other BaseFields
    public List<BaseField> Children { get; set; } = new();
    
    public bool IsCollapsible { get; set; }
    public bool IsCollapsed { get; set; }
}

/// <summary>
/// Tables with dynamic rows and columns
/// </summary>
public class TableField : BaseField
{
    public override FieldTypeDto FieldType => FieldTypeDto.Table;

    // Define the columns (Name, Area, Rate, etc.)
    public List<TableColumnDto> Columns { get; set; } = new();

    // Summary configuration for the footer
    public List<TableSummary> Summaries { get; set; } = new();

    public int MinRows { get; set; } = 1;
    public int? MaxRows { get; set; }
    public bool AllowAddRows { get; set; } = true;
    public bool AllowDeleteRows { get; set; } = true;
    public bool ShowFooter { get; set; } = true;
}

/// <summary>
/// Attachments (Images, PDFs, etc.)
/// </summary>
public class AttachmentField : BaseField
{
    public override FieldTypeDto FieldType => FieldTypeDto.FileUpload;

    public List<string>? AllowedExtensions { get; set; } = new() { ".jpg", ".png", ".pdf" };
    public long MaxFileSize { get; set; } = 5242880; // 5MB default
    public bool AllowMultiple { get; set; }

    // For Valuers: Category helps in auto-organizing the final PDF report
    public AttachmentCategoryDto Category { get; set; }
}

/// <summary>
/// Calculation rules for auto-computing field values
/// </summary>
public class CalculationRule
{
    public required string RuleId { get; set; }
    
    // Which field(s) trigger this calculation?
    public List<string> TriggerFieldIds { get; set; } = new();
    
    // The formula to execute
    public required string Formula { get; set; } 
    
    // Which field receives the result? (Matches a FieldId in the Elements tree)
    public required string TargetFieldId { get; set; }
}

/// <summary>
/// Table column definition
/// </summary>
public class TableColumnDto
{
    public required string FieldId { get; set; }
    public required string Label { get; set; }
    public FieldTypeDto FieldType { get; set; }
    public string? Width { get; set; }
    public bool IsReadonly { get; set; }
    public List<string>? Options { get; set; }
    public InputValidationRulesDto? ValidationRules { get; set; }
}

/// <summary>
/// Table summary configuration for aggregating column values
/// </summary>
public class TableSummary
{
    // The FieldId of the column to aggregate
    public required string ColumnFieldId { get; set; }
    
    public AggregateTypeDto Operation { get; set; }
    
    // Label for the footer (e.g., "Total Area")
    public string? Label { get; set; }

    // Unique ID so other CalculationFields can reference this Total
    public required string SummaryFieldId { get; set; }
}

/// <summary>
/// Visibility rules for conditional field display
/// </summary>
public class VisibilityRule
{
    // The FieldId of the field that triggers this rule
    public required string SourceFieldId { get; set; }

    // Comparison type: Equals, NotEquals, GreaterThan, Contains
    public OperatorTypeDto Operator { get; set; }

    // The value to compare against (e.g., "Commercial")
    public string? TargetValue { get; set; }
}

/// <summary>
/// Input field validation rules
/// </summary>
public class InputValidationRulesDto
{
    public double? Min { get; set; }
    public double? Max { get; set; }
    public int? MinLength { get; set; }
    public int? MaxLength { get; set; }
    public string? Pattern { get; set; }
    public string? ErrorMessage { get; set; }
}

/// <summary>
/// Bank information DTO
/// </summary>
public class BankDto
{
    public required string BankName { get; set; }
    public required string BankCode { get; set; }
}

// Enums

public enum AttachmentCategoryDto
{
    PropertyPhoto,
    LegalDocument,
    MapOrSketch,
    MarketComparison,
    ValuerSignature,
    Other
}

public enum AggregateTypeDto 
{ 
    Sum, 
    Average, 
    Min, 
    Max, 
    Count 
}

public enum OperatorTypeDto 
{ 
    Equals, 
    NotEquals, 
    GreaterThan, 
    LessThan, 
    Contains 
}

public enum ContainerTypeDto 
{ 
    Tab, 
    Group, 
    Section 
}

public enum FieldTypeDto
{
    // Inputs
    Text, 
    Number, 
    Date, 
    Dropdown, 
    FileUpload,
    Currency,
    Textarea,
    Checkbox,
    Radio,
    
    // Structure
    Tab, 
    Group, 
    Section,
    
    // Complex/Logic
    Table
}

public enum PropertyTypeDto
{
    House,
    Flat,
    Apartment,
    Land,
    Commercial,
    Other
}
