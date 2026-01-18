using System;
using System.Collections.Generic;

namespace ValuationApp.Core.DTOs;

/// <summary>
/// Request DTO for creating a custom template
/// </summary>
public class CreateCustomTemplateRequest
{
    public string TemplateName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty; // "land" or "apartment"
    public Dictionary<string, object?> FieldValues { get; set; } = new();
}

/// <summary>
/// Request DTO for updating a custom template
/// </summary>
public class UpdateCustomTemplateRequest
{
    public string? TemplateName { get; set; }
    public string? Description { get; set; }
    public Dictionary<string, object?>? FieldValues { get; set; }
}

/// <summary>
/// Complete custom template DTO with all details
/// </summary>
public class SavedCustomTemplateDto
{
    public string Id { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string BankCode { get; set; } = string.Empty;
    public string BankName { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public Dictionary<string, object?> FieldValues { get; set; } = new();
    public string CreatedBy { get; set; } = string.Empty;
    public string CreatedByName { get; set; } = string.Empty;
    public string OrganizationId { get; set; } = string.Empty;
    public bool IsActive { get; set; }
    public int Version { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

/// <summary>
/// Response for create/update operations
/// </summary>
public class CustomTemplateCreateResponse
{
    public string TemplateId { get; set; } = string.Empty;
    public SavedCustomTemplateDto Template { get; set; } = new();
}

/// <summary>
/// List item DTO for custom templates (without field values for performance)
/// </summary>
public class CustomTemplateListItemDto
{
    public string Id { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string BankCode { get; set; } = string.Empty;
    public string BankName { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public string CreatedBy { get; set; } = string.Empty;
    public string CreatedByName { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

/// <summary>
/// Response wrapper for template fields API (matches frontend expectations)
/// </summary>
public class CustomTemplateFieldsResponse
{
    public bool Success { get; set; } = true;
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public TemplateBasicInfo? TemplateInfo { get; set; }
    public List<object> CommonFields { get; set; } = new();
    public List<object> BankSpecificTabs { get; set; } = new();
}

/// <summary>
/// Template information for response
/// </summary>
public class TemplateBasicInfo
{
    public string TemplateId { get; set; } = string.Empty;
    public string TemplateCode { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public string BankCode { get; set; } = string.Empty;
    public string BankName { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
}

/// <summary>
/// DTO for custom template with default values
/// </summary>
public class CustomTemplateDto
{
    public string? Id { get; set; }
    public string OrganizationId { get; set; } = string.Empty;
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public string TemplateId { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public List<CustomFieldDefault> CustomDefaults { get; set; } = new();
    public string CreatedBy { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public bool IsActive { get; set; } = true;
}

/// <summary>
/// Represents a field with its default value in custom template
/// </summary>
public class CustomFieldDefault
{
    public string FieldId { get; set; } = string.Empty;
    public string FieldPath { get; set; } = string.Empty; // e.g., "property_details.property_part_b.owner_details"
    public string UiDisplayName { get; set; } = string.Empty;
    public string FieldType { get; set; } = string.Empty;
    public string? DefaultValue { get; set; }
    public string? HelpText { get; set; }
    public int SortOrder { get; set; }
    public string DocumentId { get; set; } = string.Empty; // e.g., "property_details"
    public string SectionId { get; set; } = string.Empty; // e.g., "property_part_b"
}

/// <summary>
/// DTO for loading template fields eligible for custom defaults
/// </summary>
public class CustomTemplateFieldsDto
{
    public string TemplateId { get; set; } = string.Empty;
    public string TemplateName { get; set; } = string.Empty;
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public List<CustomTemplateDocument> Documents { get; set; } = new();
}

/// <summary>
/// Represents a document (tab) with sections and fields
/// </summary>
public class CustomTemplateDocument
{
    public string DocumentId { get; set; } = string.Empty;
    public string DocumentName { get; set; } = string.Empty;
    public string UiName { get; set; } = string.Empty;
    public List<CustomTemplateSection> Sections { get; set; } = new();
}

/// <summary>
/// Represents a section within a document
/// </summary>
public class CustomTemplateSection
{
    public string SectionId { get; set; } = string.Empty;
    public string SectionName { get; set; } = string.Empty;
    public int SortOrder { get; set; }
    public List<CustomTemplateField> Fields { get; set; } = new();
}

/// <summary>
/// Represents a field eligible for custom default value
/// </summary>
public class CustomTemplateField
{
    public string FieldId { get; set; } = string.Empty;
    public string UiDisplayName { get; set; } = string.Empty;
    public string FieldType { get; set; } = string.Empty;
    public string? HelpText { get; set; }
    public string? Placeholder { get; set; }
    public string? DefaultValue { get; set; }
    public int SortOrder { get; set; }
    public bool IsGroup { get; set; }
    public List<CustomTemplateField>? SubFields { get; set; }
    public List<FieldOption>? Options { get; set; } // For select fields
}

/// <summary>
/// Options for select/dropdown fields
/// </summary>
public class FieldOption
{
    public string Value { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
}

/// <summary>
/// Request DTO for saving custom template
/// </summary>
public class SaveCustomTemplateRequest
{
    public string? Id { get; set; } // Null for new, populated for update
    public string OrganizationId { get; set; } = string.Empty;
    public string BankCode { get; set; } = string.Empty;
    public string PropertyType { get; set; } = string.Empty;
    public List<CustomFieldDefault> CustomDefaults { get; set; } = new();
}
