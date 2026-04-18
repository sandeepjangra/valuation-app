namespace ValuationApp.Common.Models;

/// <summary>
/// Request model for creating a new organization
/// </summary>
public class CreateOrganizationRequest
{
    public string Name { get; set; } = string.Empty;
    public string ContactEmail { get; set; } = string.Empty;
    public string? PhoneNumber { get; set; }
    public string? Address { get; set; }
    public int? MaxUsers { get; set; }
    public string? SubscriptionPlan { get; set; }
    public string? ReportReferenceInitials { get; set; }
}
