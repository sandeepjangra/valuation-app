using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Report entity representing a valuation report
/// Stored in valuation_reports database, collection determined by organization
/// </summary>
public class Report
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("report_id")]
    public string ReportId { get; set; } = string.Empty;

    [BsonElement("reference_number")]
    public string ReferenceNumber { get; set; } = string.Empty;

    [BsonElement("organization_id")]
    public string OrganizationId { get; set; } = string.Empty;

    [BsonElement("org_short_name")]
    public string OrgShortName { get; set; } = string.Empty;

    [BsonElement("bank_code")]
    public string BankCode { get; set; } = string.Empty;

    [BsonElement("bank_name")]
    public string? BankName { get; set; }

    [BsonElement("bank_branch")]
    public string? BankBranch { get; set; }

    [BsonElement("bank_branch_name")]
    public string? BankBranchName { get; set; }

    [BsonElement("template_id")]
    public string TemplateId { get; set; } = string.Empty;

    [BsonElement("template_name")]
    public string? TemplateName { get; set; }

    [BsonElement("custom_template_id")]
    public string? CustomTemplateId { get; set; }

    [BsonElement("property_type")]
    public string PropertyType { get; set; } = string.Empty;

    [BsonElement("property_address")]
    public string? PropertyAddress { get; set; }

    [BsonElement("applicant_name")]
    public string? ApplicantName { get; set; }

    [BsonElement("loan_amount")]
    public decimal? LoanAmount { get; set; }

    [BsonElement("status")]
    public string Status { get; set; } = "draft"; // draft, in_progress, submitted, completed, approved, rejected

    [BsonElement("report_data")]
    public Dictionary<string, object>? ReportData { get; set; }

    [BsonElement("form_data")]
    public Dictionary<string, object>? FormData { get; set; }

    [BsonElement("calculated_fields")]
    public Dictionary<string, object>? CalculatedFields { get; set; }

    [BsonElement("validation_errors")]
    public List<string>? ValidationErrors { get; set; }

    [BsonElement("created_by")]
    public string CreatedBy { get; set; } = string.Empty;

    [BsonElement("created_by_email")]
    public string CreatedByEmail { get; set; } = string.Empty;

    [BsonElement("assigned_to")]
    public string? AssignedTo { get; set; }

    [BsonElement("assigned_to_email")]
    public string? AssignedToEmail { get; set; }

    [BsonElement("created_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("updated_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("submitted_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? SubmittedAt { get; set; }

    [BsonElement("completed_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? CompletedAt { get; set; }

    [BsonElement("version")]
    public int Version { get; set; } = 1;

    [BsonElement("workflow")]
    public ReportWorkflow? Workflow { get; set; }

    [BsonElement("template_structure")]
    public object? TemplateStructure { get; set; }

    [BsonElement("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Report workflow status and approvals
/// </summary>
public class ReportWorkflow
{
    [BsonElement("status")]
    public string Status { get; set; } = "DRAFT";

    [BsonElement("submitted_by")]
    public string? SubmittedBy { get; set; }

    [BsonElement("submitted_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? SubmittedAt { get; set; }

    [BsonElement("reviewed_by")]
    public string? ReviewedBy { get; set; }

    [BsonElement("reviewed_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? ReviewedAt { get; set; }

    [BsonElement("approved_by")]
    public string? ApprovedBy { get; set; }

    [BsonElement("approved_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? ApprovedAt { get; set; }

    [BsonElement("rejection_reason")]
    public string? RejectionReason { get; set; }
}
