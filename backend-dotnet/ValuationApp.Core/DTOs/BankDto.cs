using System.Text.Json.Serialization;

namespace ValuationApp.Core.DTOs;

/// <summary>
/// Bank DTO for API responses
/// </summary>
public class BankResponseDto
{
    public required string Id { get; set; }
    public required string BankId { get; set; }
    public required string BankCode { get; set; }
    public required string BankName { get; set; }
    public required string BankShortName { get; set; }
    public required string BankType { get; set; }
    public bool IsActive { get; set; }
    
    public HeadquartersDto? Headquarters { get; set; }
    public int? TotalBranches { get; set; }
    public List<BranchDto> Branches { get; set; } = new();
    public List<TemplateReferenceDto> Templates { get; set; } = new();
    
    // Migration metadata
    public string? MigratedFrom { get; set; }
    public DateTime? MigrationDate { get; set; }
    public string? MigrationScript { get; set; }
}

/// <summary>
/// Headquarters information
/// </summary>
public class HeadquartersDto
{
    public required string City { get; set; }
    public required string State { get; set; }
    public string? Pincode { get; set; }
}

/// <summary>
/// Branch information
/// </summary>
public class BranchDto
{
    public required string BranchId { get; set; }
    public required string BranchCode { get; set; }
    public required string BranchName { get; set; }
    public BranchAddressDto? BranchAddress { get; set; }
    public string? IfscCode { get; set; }
    public ContactDto? ContactDetails { get; set; }
    public bool IsActive { get; set; } = true;
}

/// <summary>
/// Branch address information
/// </summary>
public class BranchAddressDto
{
    public string? Street { get; set; }
    public required string City { get; set; }
    public required string State { get; set; }
    public string? Pincode { get; set; }
    public string? Country { get; set; }
}

/// <summary>
/// Contact information
/// </summary>
public class ContactDto
{
    public string? Phone { get; set; }
    public string? Email { get; set; }
    public string? Website { get; set; }
}

/// <summary>
/// Template reference in bank
/// </summary>
public class TemplateReferenceDto
{
    public required string TemplateId { get; set; }
    public required string PropertyType { get; set; }
    public string? TemplateName { get; set; }
    public bool IsActive { get; set; } = true;
}
