using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// Permission template defining what each role can do
/// </summary>
public class PermissionTemplate
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("role")]
    public string Role { get; set; } = string.Empty;

    [BsonElement("displayName")]
    public string DisplayName { get; set; } = string.Empty;

    [BsonElement("description")]
    public string Description { get; set; } = string.Empty;

    [BsonElement("isSystemWide")]
    public bool IsSystemWide { get; set; }

    [BsonElement("permissions")]
    public PermissionSet Permissions { get; set; } = new();

    [BsonElement("createdAt")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("updatedAt")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

public class PermissionSet
{
    [BsonElement("organizations")]
    public OrganizationPermissions Organizations { get; set; } = new();

    [BsonElement("users")]
    public RoleBasedUserPermissions Users { get; set; } = new();

    [BsonElement("reports")]
    public ReportPermissions Reports { get; set; } = new();

    [BsonElement("templates")]
    public TemplatePermissions Templates { get; set; } = new();

    [BsonElement("drafts")]
    public DraftPermissions Drafts { get; set; } = new();

    [BsonElement("analytics")]
    public AnalyticsPermissions Analytics { get; set; } = new();

    [BsonElement("settings")]
    public SettingsPermissions Settings { get; set; } = new();
}

public class OrganizationPermissions
{
    [BsonElement("viewAll")]
    public bool ViewAll { get; set; }

    [BsonElement("create")]
    public bool Create { get; set; }

    [BsonElement("editAny")]
    public bool EditAny { get; set; }

    [BsonElement("delete")]
    public bool Delete { get; set; }

    [BsonElement("manageSettings")]
    public bool ManageSettings { get; set; }
}

public class RoleBasedUserPermissions
{
    [BsonElement("viewAllOrgs")]
    public bool ViewAllOrgs { get; set; }

    [BsonElement("viewOwnOrg")]
    public bool ViewOwnOrg { get; set; }

    [BsonElement("create")]
    public bool Create { get; set; }

    [BsonElement("editAny")]
    public bool EditAny { get; set; }

    [BsonElement("deleteAny")]
    public bool DeleteAny { get; set; }

    [BsonElement("viewActivity")]
    public bool ViewActivity { get; set; }

    [BsonElement("manageRoles")]
    public bool ManageRoles { get; set; }
}

public class ReportPermissions
{
    [BsonElement("create")]
    public bool Create { get; set; }

    [BsonElement("editOwn")]
    public bool EditOwn { get; set; }

    [BsonElement("editOthers")]
    public bool EditOthers { get; set; }

    [BsonElement("deleteOwn")]
    public bool DeleteOwn { get; set; }

    [BsonElement("deleteOthers")]
    public bool DeleteOthers { get; set; }

    [BsonElement("viewDrafts")]
    public bool ViewDrafts { get; set; }

    [BsonElement("saveDraft")]
    public bool SaveDraft { get; set; }

    [BsonElement("submit")]
    public bool Submit { get; set; }

    [BsonElement("viewAllOrg")]
    public bool ViewAllOrg { get; set; }

    [BsonElement("viewAllOrgs")]
    public bool ViewAllOrgs { get; set; }

    [BsonElement("export")]
    public bool Export { get; set; }
}

public class TemplatePermissions
{
    [BsonElement("view")]
    public bool View { get; set; }

    [BsonElement("viewBankTemplates")]
    public bool ViewBankTemplates { get; set; }

    [BsonElement("createCustom")]
    public bool CreateCustom { get; set; }

    [BsonElement("editCustom")]
    public bool EditCustom { get; set; }

    [BsonElement("deleteCustom")]
    public bool DeleteCustom { get; set; }

    [BsonElement("manageBankTemplates")]
    public bool ManageBankTemplates { get; set; }

    [BsonElement("shareAcrossOrgs")]
    public bool ShareAcrossOrgs { get; set; }
}

public class DraftPermissions
{
    [BsonElement("create")]
    public bool Create { get; set; }

    [BsonElement("editOwn")]
    public bool EditOwn { get; set; }

    [BsonElement("editOthers")]
    public bool EditOthers { get; set; }

    [BsonElement("viewOwn")]
    public bool ViewOwn { get; set; }

    [BsonElement("viewOthers")]
    public bool ViewOthers { get; set; }

    [BsonElement("deleteOwn")]
    public bool DeleteOwn { get; set; }

    [BsonElement("deleteOthers")]
    public bool DeleteOthers { get; set; }
}

public class AnalyticsPermissions
{
    [BsonElement("viewOwnActivity")]
    public bool ViewOwnActivity { get; set; }

    [BsonElement("viewOrgActivity")]
    public bool ViewOrgActivity { get; set; }

    [BsonElement("viewAllActivity")]
    public bool ViewAllActivity { get; set; }

    [BsonElement("exportReports")]
    public bool ExportReports { get; set; }
}

public class SettingsPermissions
{
    [BsonElement("editOrgSettings")]
    public bool EditOrgSettings { get; set; }

    [BsonElement("editSystemSettings")]
    public bool EditSystemSettings { get; set; }

    [BsonElement("manageIntegrations")]
    public bool ManageIntegrations { get; set; }

    [BsonElement("viewLogs")]
    public bool ViewLogs { get; set; }
}
