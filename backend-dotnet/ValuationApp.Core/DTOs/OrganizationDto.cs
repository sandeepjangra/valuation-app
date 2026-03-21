namespace ValuationApp.Core.DTOs;

/// <summary>
/// Organization DTO for API responses
/// </summary>
public class OrganizationResponseDto
{
    public required string Id { get; set; }
    public required string OrganizationId { get; set; }
    public required string ShortName { get; set; }
    public required string FullName { get; set; }
    public string? Description { get; set; }
    public string? ReportReferenceInitials { get; set; }
    public int LastReferenceNumber { get; set; }
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public bool IsActive { get; set; } = true;
    
    public DateTime? CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    
    // Migration metadata
    public string? MigratedFrom { get; set; }
    public DateTime? MigrationDate { get; set; }
    public string? MigrationScript { get; set; }
}

/// <summary>
/// Organization creation/update request DTO
/// </summary>
public class OrganizationRequestDto
{
    public required string ShortName { get; set; }
    public required string FullName { get; set; }
    public string? Description { get; set; }
    public string? ReportReferenceInitials { get; set; }
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public bool IsActive { get; set; } = true;
}
