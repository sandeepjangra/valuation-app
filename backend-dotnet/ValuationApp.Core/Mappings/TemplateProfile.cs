using AutoMapper;
using ValuationApp.Core.Entities;
using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Mappings;

/// <summary>
/// AutoMapper profile for mapping between entities and DTOs
/// </summary>
public class TemplateProfile : Profile
{
    public TemplateProfile()
    {
        ConfigureTemplateMapping();
        ConfigureBankMapping();
        ConfigureOrganizationMapping();
    }

    private void ConfigureTemplateMapping()
    {
        // ── Template ──────────────────────────────────────────────────────────
        CreateMap<Template, ValuationTemplate>()
            .ForMember(dest => dest.PropertyType, opt => opt.MapFrom(src => MapPropertyType(src.PropertyType)))
            .ForMember(dest => dest.Elements,     opt => opt.MapFrom(src => MapElements(src.Elements)))
            .ReverseMap()
            .ForMember(dest => dest.PropertyType, opt => opt.MapFrom(src => src.PropertyType.ToString()))
            .ForMember(dest => dest.Elements,     opt => opt.Ignore()); // reverse handled manually if needed

        // ── BankDetails ───────────────────────────────────────────────────────
        CreateMap<BankDetails, BankDto>().ReverseMap();

        // ── Validation rules ──────────────────────────────────────────────────
        CreateMap<InputValidationRules, InputValidationRulesDto>()
            .ForMember(dest => dest.ErrorMessage, opt => opt.MapFrom(src => src.CustomMessage))
            .ReverseMap()
            .ForMember(dest => dest.CustomMessage, opt => opt.MapFrom(src => src.ErrorMessage));

        // ── Calculation rules ─────────────────────────────────────────────────
        CreateMap<Entities.CalculationRule, DTOs.CalculationRule>().ReverseMap();

        // ── TableColumn ───────────────────────────────────────────────────────
        // Entity Options is List<FieldOption>, DTO Options is List<string>
        CreateMap<TableColumn, TableColumnDto>()
            .ForMember(dest => dest.FieldType, opt => opt.MapFrom(src => MapFieldType(src.FieldType)))
            .ForMember(dest => dest.Options,   opt => opt.MapFrom(src => MapOptions(src.Options)))
            .ReverseMap()
            .ForMember(dest => dest.FieldType, opt => opt.MapFrom(src => src.FieldType.ToString()))
            .ForMember(dest => dest.Options,   opt => opt.Ignore());
    }

    private void ConfigureBankMapping()
    {
        CreateMap<Bank, BankResponseDto>();
        CreateMap<HeadquartersInfo, HeadquartersDto>().ReverseMap();
        CreateMap<BranchEntity, BranchDto>()
            .ForMember(dest => dest.BranchAddress,  opt => opt.MapFrom(src => src.BranchAddress))
            .ForMember(dest => dest.ContactDetails, opt => opt.MapFrom(src => src.ContactDetails))
            .ReverseMap();
        CreateMap<BranchAddressInfo, BranchAddressDto>().ReverseMap();
        CreateMap<ContactInfo, ContactDto>().ReverseMap();
        CreateMap<TemplateReference, TemplateReferenceDto>().ReverseMap();
    }

    private void ConfigureOrganizationMapping()
    {
        CreateMap<Organization, OrganizationResponseDto>();
        CreateMap<OrganizationRequestDto, Organization>()
            .ForMember(dest => dest.Id,                opt => opt.Ignore())
            .ForMember(dest => dest.OrganizationId,    opt => opt.Ignore())
            .ForMember(dest => dest.LastReferenceNumber, opt => opt.Ignore())
            .ForMember(dest => dest.CreatedAt,         opt => opt.Ignore())
            .ForMember(dest => dest.UpdatedAt,         opt => opt.Ignore())
            .ForMember(dest => dest.MigratedFrom,      opt => opt.Ignore())
            .ForMember(dest => dest.MigrationDate,     opt => opt.Ignore())
            .ForMember(dest => dest.MigrationScript,   opt => opt.Ignore());
    }

    // ── Element tree mapping ──────────────────────────────────────────────────
    // AutoMapper cannot handle polymorphic abstract→concrete mapping automatically,
    // so we map the element tree manually via a recursive helper.

    private List<BaseField> MapElements(List<TemplateElement> elements)
    {
        var result = new List<BaseField>();
        foreach (var element in elements)
            result.Add(MapElement(element));
        return result;
    }

    private BaseField MapElement(TemplateElement element)
    {
        return element switch
        {
            InputElement input       => MapInputElement(input),
            TableElement table       => MapTableElement(table),
            ContainerElement container => MapContainerElement(container),
            _ => throw new InvalidOperationException($"Unknown element type: {element.GetType().Name}")
        };
    }

    private InputField MapInputElement(InputElement src)
    {
        return new InputField
        {
            FieldId         = src.FieldId,
            Label           = src.Label,
            DisplayOrder    = src.DisplayOrder,
            IsVisible       = src.IsVisible,
            SpecificType    = MapFieldType(src.SpecificType),
            IsRequired      = src.IsRequired,
            IsReadonly      = src.IsReadonly,
            DefaultValue    = src.DefaultValue?.ToString(),
            HelpText        = src.HelpText,
            PlaceholderText = src.PlaceholderText,
            Options         = MapOptions(src.Options),
            ValidationRules = src.ValidationRules is null ? null : new InputValidationRulesDto
            {
                Min          = src.ValidationRules.Min,
                Max          = src.ValidationRules.Max,
                MinLength    = src.ValidationRules.MinLength,
                MaxLength    = src.ValidationRules.MaxLength,
                Pattern      = src.ValidationRules.Pattern,
                ErrorMessage = src.ValidationRules.CustomMessage
            }
        };
    }

    private TableField MapTableElement(TableElement src)
    {
        return new TableField
        {
            FieldId          = src.FieldId,
            Label            = src.Label,
            DisplayOrder     = src.DisplayOrder,
            IsVisible        = src.IsVisible,
            Columns          = src.Columns.Select(MapTableColumn).ToList(),
            Summaries        = new List<TableSummary>(), // TODO: persist summaries in entity
            MinRows          = src.MinRows,
            MaxRows          = src.MaxRows,
            AllowAddRows     = src.AllowAddRows,
            AllowDeleteRows  = src.AllowDeleteRows,
            ShowFooter       = src.Columns.Count > 0 // default: show footer when columns exist
        };
    }

    private TableColumnDto MapTableColumn(TableColumn src)
    {
        return new TableColumnDto
        {
            FieldId    = src.FieldId,
            Label      = src.Label,
            FieldType  = MapFieldType(src.FieldType),
            Width      = src.Width,
            IsReadonly = src.IsReadonly,
            Options    = MapOptions(src.Options),
            ValidationRules = src.ValidationRules is null ? null : new InputValidationRulesDto
            {
                Min          = src.ValidationRules.Min,
                Max          = src.ValidationRules.Max,
                MinLength    = src.ValidationRules.MinLength,
                MaxLength    = src.ValidationRules.MaxLength,
                Pattern      = src.ValidationRules.Pattern,
                ErrorMessage = src.ValidationRules.CustomMessage
            }
        };
    }

    /// <summary>
    /// Maps a ContainerElement to the correct concrete DTO subtype based on ContainerType string.
    /// Hierarchy:
    ///   "tabgroup" → TabGroupField  (children are TabField[])
    ///   "tab"      → TabField       (children are BaseField[])
    ///   "section"  → SectionField   (children are BaseField[])
    ///   "group"    → GroupField     (children are BaseField[])
    /// </summary>
    private ContainerField MapContainerElement(ContainerElement src)
    {
        var containerType = src.ContainerType?.ToLower();

        return containerType switch
        {
            "tabgroup" => new TabGroupField
            {
                FieldId      = src.FieldId,
                Label        = src.Label,
                DisplayOrder = src.DisplayOrder,
                IsVisible    = src.IsVisible,
                // Children must all be TabField — filter and cast
                Children     = src.Children
                    .OfType<ContainerElement>()
                    .Where(c => c.ContainerType?.ToLower() == "tab")
                    .Select(c => (TabField)MapContainerElement(c))
                    .ToList()
            },

            "tab" => new TabField
            {
                FieldId      = src.FieldId,
                Label        = src.Label,
                DisplayOrder = src.DisplayOrder,
                IsVisible    = src.IsVisible,
                Children     = MapElements(src.Children)
            },

            "section" => new SectionField
            {
                FieldId       = src.FieldId,
                Label         = src.Label,
                DisplayOrder  = src.DisplayOrder,
                IsVisible     = src.IsVisible,
                Children      = MapElements(src.Children),
                IsCollapsible = src.IsCollapsible,
                IsCollapsed   = src.IsCollapsed
            },

            "group" => new GroupField
            {
                FieldId       = src.FieldId,
                Label         = src.Label,
                DisplayOrder  = src.DisplayOrder,
                IsVisible     = src.IsVisible,
                Children      = MapElements(src.Children),
                IsCollapsible = src.IsCollapsible,
                IsCollapsed   = src.IsCollapsed
            },

            // Fallback: treat unknown container types as a section
            _ => new SectionField
            {
                FieldId       = src.FieldId,
                Label         = src.Label,
                DisplayOrder  = src.DisplayOrder,
                IsVisible     = src.IsVisible,
                Children      = MapElements(src.Children),
                IsCollapsible = src.IsCollapsible,
                IsCollapsed   = src.IsCollapsed
            }
        };
    }

    // ── Option helpers ────────────────────────────────────────────────────────

    /// <summary>
    /// Entity stores options as List&lt;FieldOption&gt; (Value + Label).
    /// DTO expects List&lt;string&gt; — we use the Label for display.
    /// </summary>
    private static List<string>? MapOptions(List<Entities.FieldOption>? options)
    {
        if (options is null || options.Count == 0) return null;
        
        return options.Select(o => string.IsNullOrWhiteSpace(o.Label) ? o.Value : o.Label).ToList();
    }

    // ── Enum helpers ──────────────────────────────────────────────────────────

    private static PropertyTypeDto MapPropertyType(string propertyType) =>
        propertyType?.ToLower() switch
        {
            "house"      => PropertyTypeDto.House,
            "flat"       => PropertyTypeDto.Flat,
            "apartment"  => PropertyTypeDto.Apartment,
            "land"       => PropertyTypeDto.Land,
            "commercial" => PropertyTypeDto.Commercial,
            _            => PropertyTypeDto.Other
        };

    private static FieldTypeDto MapFieldType(string fieldType) =>
        fieldType?.ToLower() switch
        {
            "text"       => FieldTypeDto.Text,
            "number"     => FieldTypeDto.Number,
            "date"       => FieldTypeDto.Date,
            "dropdown"   => FieldTypeDto.Dropdown,
            "fileupload" => FieldTypeDto.FileUpload,
            "currency"   => FieldTypeDto.Currency,
            "textarea"   => FieldTypeDto.Textarea,
            "checkbox"   => FieldTypeDto.Checkbox,
            "radio"      => FieldTypeDto.Radio,
            "table"      => FieldTypeDto.Table,
            // container types no longer map to FieldTypeDto — they use FieldTypeDto.Container
            _            => FieldTypeDto.Text
        };
}
