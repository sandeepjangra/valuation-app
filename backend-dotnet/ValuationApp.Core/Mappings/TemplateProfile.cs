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
        // Main Template mapping
        CreateMap<Template, ValuationTemplate>()
            .ForMember(dest => dest.PropertyType, opt => opt.MapFrom(src => MapPropertyType(src.PropertyType)))
            .ReverseMap()
            .ForMember(dest => dest.PropertyType, opt => opt.MapFrom(src => src.PropertyType.ToString()));

        // BankDetails mapping
        CreateMap<BankDetails, BankDto>().ReverseMap();

        // Base field mapping - polymorphic handling
        CreateMap<TemplateElement, BaseField>()
            .Include<InputElement, InputField>()
            .Include<ContainerElement, ContainerField>()
            .Include<TableElement, TableField>();

        // InputElement to InputField
        CreateMap<InputElement, InputField>()
            .ForMember(dest => dest.SpecificType, opt => opt.MapFrom(src => MapFieldType(src.SpecificType)))
            .ForMember(dest => dest.ValidationRules, opt => opt.MapFrom(src => src.ValidationRules))
            .ReverseMap()
            .ForMember(dest => dest.SpecificType, opt => opt.MapFrom(src => src.SpecificType.ToString()));

        // ContainerElement to ContainerField
        CreateMap<ContainerElement, ContainerField>()
            .ForMember(dest => dest.Container, opt => opt.MapFrom(src => MapContainerType(src.ContainerType)))
            .ReverseMap()
            .ForMember(dest => dest.ContainerType, opt => opt.MapFrom(src => src.Container.ToString()));

        // TableElement to TableField
        CreateMap<TableElement, TableField>()
            .ForMember(dest => dest.Columns, opt => opt.MapFrom(src => src.Columns))
            .ForMember(dest => dest.Summaries, opt => opt.MapFrom(src => new List<TableSummary>())) // TODO: Implement table summaries
            .ReverseMap();

        // TableColumn mapping
        CreateMap<TableColumn, TableColumnDto>()
            .ForMember(dest => dest.FieldType, opt => opt.MapFrom(src => MapFieldType(src.FieldType)))
            .ReverseMap()
            .ForMember(dest => dest.FieldType, opt => opt.MapFrom(src => src.FieldType.ToString()));

        // Validation rules mapping
        CreateMap<InputValidationRules, InputValidationRulesDto>().ReverseMap();

        // Calculation rules mapping
        CreateMap<Entities.CalculationRule, DTOs.CalculationRule>().ReverseMap();
    }

    private void ConfigureBankMapping()
    {
        // Bank entity to DTO
        CreateMap<Bank, BankResponseDto>();

        // Nested mappings for bank
        CreateMap<HeadquartersInfo, HeadquartersDto>().ReverseMap();
        CreateMap<BranchEntity, BranchDto>()
            .ForMember(dest => dest.BranchAddress, opt => opt.MapFrom(src => src.BranchAddress))
            .ForMember(dest => dest.ContactDetails, opt => opt.MapFrom(src => src.ContactDetails))
            .ReverseMap();
        CreateMap<BranchAddressInfo, BranchAddressDto>().ReverseMap();
        CreateMap<ContactInfo, ContactDto>().ReverseMap();
        CreateMap<TemplateReference, TemplateReferenceDto>().ReverseMap();
    }

    private void ConfigureOrganizationMapping()
    {
        // Organization entity to DTO
        CreateMap<Organization, OrganizationResponseDto>();
        
        // Organization request DTO to entity
        CreateMap<OrganizationRequestDto, Organization>()
            .ForMember(dest => dest.Id, opt => opt.Ignore())
            .ForMember(dest => dest.OrganizationId, opt => opt.Ignore())
            .ForMember(dest => dest.LastReferenceNumber, opt => opt.Ignore())
            .ForMember(dest => dest.CreatedAt, opt => opt.Ignore())
            .ForMember(dest => dest.UpdatedAt, opt => opt.Ignore())
            .ForMember(dest => dest.MigratedFrom, opt => opt.Ignore())
            .ForMember(dest => dest.MigrationDate, opt => opt.Ignore())
            .ForMember(dest => dest.MigrationScript, opt => opt.Ignore());
    }

    // Helper methods for enum mapping
    private PropertyTypeDto MapPropertyType(string propertyType)
    {
        return propertyType?.ToLower() switch
        {
            "house" => PropertyTypeDto.House,
            "flat" => PropertyTypeDto.Flat,
            "apartment" => PropertyTypeDto.Apartment,
            "land" => PropertyTypeDto.Land,
            "commercial" => PropertyTypeDto.Commercial,
            _ => PropertyTypeDto.Other
        };
    }

    private FieldTypeDto MapFieldType(string fieldType)
    {
        return fieldType?.ToLower() switch
        {
            "text" => FieldTypeDto.Text,
            "number" => FieldTypeDto.Number,
            "date" => FieldTypeDto.Date,
            "dropdown" => FieldTypeDto.Dropdown,
            "fileupload" => FieldTypeDto.FileUpload,
            "currency" => FieldTypeDto.Currency,
            "textarea" => FieldTypeDto.Textarea,
            "checkbox" => FieldTypeDto.Checkbox,
            "radio" => FieldTypeDto.Radio,
            "tab" => FieldTypeDto.Tab,
            "group" => FieldTypeDto.Group,
            "section" => FieldTypeDto.Section,
            "table" => FieldTypeDto.Table,
            _ => FieldTypeDto.Text
        };
    }

    private ContainerTypeDto MapContainerType(string containerType)
    {
        return containerType?.ToLower() switch
        {
            "tab" => ContainerTypeDto.Tab,
            "group" => ContainerTypeDto.Group,
            "section" => ContainerTypeDto.Section,
            _ => ContainerTypeDto.Section
        };
    }
}
