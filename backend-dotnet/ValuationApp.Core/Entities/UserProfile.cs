using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ValuationApp.Core.Entities;

/// <summary>
/// UserProfile entity for organization-specific user metadata
/// Stored in {orgShortName}.user_profiles collection
/// </summary>
public class UserProfile
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("user_id")]
    public string UserId { get; set; } = string.Empty;

    [BsonElement("email")]
    public string Email { get; set; } = string.Empty;

    [BsonElement("org_short_name")]
    public string OrgShortName { get; set; } = string.Empty;

    [BsonElement("last_login")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? LastLogin { get; set; }

    [BsonElement("login_count")]
    public int LoginCount { get; set; } = 0;

    [BsonElement("reports_created")]
    public int ReportsCreated { get; set; } = 0;

    [BsonElement("reports_submitted")]
    public int ReportsSubmitted { get; set; } = 0;

    [BsonElement("last_activity")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime? LastActivity { get; set; }

    [BsonElement("preferences")]
    public UserPreferences? Preferences { get; set; }

    [BsonElement("activity_logs")]
    public List<ActivityLog>? ActivityLogs { get; set; }

    [BsonElement("created_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [BsonElement("updated_at")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// User preferences for the organization
/// </summary>
public class UserPreferences
{
    [BsonElement("theme")]
    public string? Theme { get; set; }

    [BsonElement("language")]
    public string Language { get; set; } = "en";

    [BsonElement("notifications_enabled")]
    public bool NotificationsEnabled { get; set; } = true;

    [BsonElement("default_bank")]
    public string? DefaultBank { get; set; }

    [BsonElement("dashboard_layout")]
    public Dictionary<string, object>? DashboardLayout { get; set; }
}

/// <summary>
/// Activity log entry for user actions
/// </summary>
public class ActivityLog
{
    [BsonElement("action")]
    public string Action { get; set; } = string.Empty;

    [BsonElement("resource_type")]
    public string? ResourceType { get; set; }

    [BsonElement("resource_id")]
    public string? ResourceId { get; set; }

    [BsonElement("details")]
    public string? Details { get; set; }

    [BsonElement("timestamp")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    [BsonElement("ip_address")]
    public string? IpAddress { get; set; }

    [BsonElement("user_agent")]
    public string? UserAgent { get; set; }
}
