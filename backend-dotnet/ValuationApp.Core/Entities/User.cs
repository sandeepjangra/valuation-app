using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// User entity representing a user in the valuation_admin.users collection
/// </summary>
public class User
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("user_id")]
    public string UserId { get; set; } = string.Empty;

    [BsonElement("email")]
    public string Email { get; set; } = string.Empty;

    [BsonElement("full_name")]
    public string FullName { get; set; } = string.Empty;

    [BsonElement("phone")]
    public string? Phone { get; set; }

    [BsonElement("password_hash")]
    public string PasswordHash { get; set; } = string.Empty;

    [BsonElement("organization_id")]
    public string OrganizationId { get; set; } = string.Empty;

    [BsonElement("org_short_name")]
    public string? OrgShortName { get; set; }

    [BsonElement("organization_name")]
    public string? OrganizationName { get; set; }

    [BsonElement("role")]
    public string Role { get; set; } = string.Empty;

    [BsonElement("roles")]
    public List<string> Roles { get; set; } = new();

    [BsonElement("status")]
    public string Status { get; set; } = "active";

    [BsonElement("is_active")]
    public bool IsActive { get; set; } = true;

    [BsonElement("is_system_admin")]
    public bool IsSystemAdmin { get; set; } = false;

    [BsonElement("department")]
    public string? Department { get; set; }

    [BsonElement("permissions")]
    public UserPermissions? Permissions { get; set; }

    [BsonElement("created_by")]
    public string? CreatedBy { get; set; }

    [BsonElement("created_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("updated_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("last_login")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? LastLogin { get; set; }
}

/// <summary>
/// User permissions model
/// </summary>
public class UserPermissions
{
    [BsonElement("can_submit_reports")]
    public bool CanSubmitReports { get; set; } = false;

    [BsonElement("can_manage_users")]
    public bool CanManageUsers { get; set; } = false;

    [BsonElement("is_manager")]
    public bool IsManager { get; set; } = false;

    [BsonElement("is_admin")]
    public bool IsAdmin { get; set; } = false;
}
