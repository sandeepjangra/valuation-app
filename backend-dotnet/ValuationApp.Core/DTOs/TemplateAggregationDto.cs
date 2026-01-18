namespace ValuationApp.Core.DTOs;

/// <summary>
/// Request to get aggregated template data
/// </summary>
public class TemplateAggregationRequest
{
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty; // "land" or "apartment"
}

/// <summary>
/// Aggregated template response with all necessary data
/// </summary>
public class AggregatedTemplateResponse
{
    public BankInfo Bank { get; set; } = new();
    public TemplateInfo Template { get; set; } = new();
    public TemplateStructure TemplateStructure { get; set; } = new();
    public List<DocumentType> DocumentTypes { get; set; } = new();
    public CommonFields CommonFields { get; set; } = new();
}

public class BankInfo
{
    public string BankId { get; set; } = string.Empty;
    public string BankCode { get; set; } = string.Empty;
    public string BankName { get; set; } = string.Empty;
    public string BankShortName { get; set; } = string.Empty;
}

public class TemplateInfo
{
    public string TemplateId { get; set; } = string.Empty;
    public string TemplateCode { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public string CollectionRef { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
}

public class TemplateStructure
{
    public TemplateMetadata? Metadata { get; set; }
    public TemplateMetadataDetails? TemplateMetadata { get; set; }
    public List<Tab>? Tabs { get; set; }
}

public class TemplateMetadata
{
    public string? GeneratedAt { get; set; }
    public string? CollectionName { get; set; }
    public int? TotalDocuments { get; set; }
    public int? Version { get; set; }
    public string? Database { get; set; }
    public string? Description { get; set; }
    public string? BankCode { get; set; }
}

public class TemplateMetadataDetails
{
    public string? TemplateId { get; set; }
    public string? TemplateName { get; set; }
    public string? BankCode { get; set; }
    public string? PropertyType { get; set; }
    public string? Version { get; set; }
    public List<Tab>? Tabs { get; set; }
}

public class Tab
{
    public string TabId { get; set; } = string.Empty;
    public string TabName { get; set; } = string.Empty;
    public string? DocumentSource { get; set; }
    public int SortOrder { get; set; }
    public bool HasSections { get; set; }
    public List<Section>? Sections { get; set; }
    public List<Field>? Fields { get; set; } // For tabs without sections
    public string? Description { get; set; }
}

public class Section
{
    public string SectionId { get; set; } = string.Empty;
    public string SectionName { get; set; } = string.Empty;
    public int SortOrder { get; set; }
    public string? Description { get; set; }
    public List<Field>? Fields { get; set; }
    public bool? UseDocumentCollection { get; set; }
    public List<string>? OriginalFields { get; set; }
    public object? DocumentFilter { get; set; }
}

public class Field
{
    public string FieldId { get; set; } = string.Empty;
    public string TechnicalName { get; set; } = string.Empty;
    public string UiDisplayName { get; set; } = string.Empty;
    public string FieldType { get; set; } = string.Empty;
    public bool IsRequired { get; set; }
    public string? Placeholder { get; set; }
    public string? HelpText { get; set; }
    public object? Validation { get; set; }
    public int? GridSize { get; set; }
    public int? SortOrder { get; set; }
    public bool IsActive { get; set; }
    public string? DefaultValue { get; set; }
    public object? Options { get; set; } // Can be string[] or FieldOption[]
    public string? DataSource { get; set; }
    public object? DataSourceConfig { get; set; }
    public bool? IsReadonly { get; set; }
    public bool? IncludeInCustomTemplate { get; set; }
    public List<Field>? SubFields { get; set; } // For group fields
    
    // Table-specific properties
    public object? TableConfig { get; set; } // Configuration for dynamic tables
    public List<object>? Columns { get; set; } // Column definitions for static tables
    public List<object>? Rows { get; set; } // Row data for static tables
}

public class DocumentType
{
    public string DocumentId { get; set; } = string.Empty;
    public string DocumentName { get; set; } = string.Empty;
    public string TechnicalName { get; set; } = string.Empty;
    public string FieldType { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public List<string> ApplicablePropertyTypes { get; set; } = new();
    public List<string> ApplicableBanks { get; set; } = new();
    public bool IsRequired { get; set; }
    public bool IsActive { get; set; }
    public int SortOrder { get; set; }
    public object? Validation { get; set; }
    public string? HelpText { get; set; }
    public string? Placeholder { get; set; }
}

public class CommonFields
{
    public string CollectionName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public List<Field> Fields { get; set; } = new();
}
