namespace ValuationApp.Common.Models;

/// <summary>
/// Request model for updating organization details
/// </summary>
public class UpdateOrganizationRequest
{
    public string? FullName { get; set; }
    public string? Description { get; set; }
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public string? ReportReferenceInitials { get; set; }
    public bool? IsActive { get; set; }
}
