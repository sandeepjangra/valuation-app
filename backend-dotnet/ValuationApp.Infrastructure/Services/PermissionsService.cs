using Microsoft.Extensions.Logging;
using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Services;

public class PermissionsService : IPermissionsService
{
    private readonly MongoDbContext _context;
    private readonly ILogger<PermissionsService> _logger;
    private readonly IMongoCollection<PermissionTemplate> _permissionsCollection;

    public PermissionsService(
        MongoDbContext context,
        ILogger<PermissionsService> logger)
    {
        _context = context;
        _logger = logger;
        _permissionsCollection = _context.AdminDatabase.GetCollection<PermissionTemplate>("permissions_templates");
    }

    public async Task<PermissionTemplate?> GetPermissionTemplateAsync(string role)
    {
        _logger.LogInformation("Getting permission template for role: {Role}", role);
        
        var filter = Builders<PermissionTemplate>.Filter.Eq(pt => pt.Role, role);
        return await _permissionsCollection.Find(filter).FirstOrDefaultAsync();
    }

    public async Task<List<PermissionTemplate>> GetAllPermissionTemplatesAsync()
    {
        _logger.LogInformation("Getting all permission templates");
        return await _permissionsCollection.Find(_ => true).ToListAsync();
    }

    public async Task SeedPermissionTemplatesAsync()
    {
        _logger.LogInformation("Seeding permission templates...");

        // Check if templates already exist
        var count = await _permissionsCollection.CountDocumentsAsync(_ => true);
        if (count > 0)
        {
            _logger.LogInformation("Permission templates already exist. Skipping seed.");
            return;
        }

        var templates = new List<PermissionTemplate>
        {
            // SYSTEM ADMIN
            new PermissionTemplate
            {
                Role = "system_admin",
                DisplayName = "System Administrator",
                Description = "Complete access across all organizations and system-wide settings",
                IsSystemWide = true,
                Permissions = new PermissionSet
                {
                    Organizations = new OrganizationPermissions
                    {
                        ViewAll = true,
                        Create = true,
                        EditAny = true,
                        Delete = true,
                        ManageSettings = true
                    },
                    Users = new RoleBasedUserPermissions
                    {
                        ViewAllOrgs = true,
                        ViewOwnOrg = true,
                        Create = true,
                        EditAny = true,
                        DeleteAny = true,
                        ViewActivity = true,
                        ManageRoles = true
                    },
                    Reports = new ReportPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true,
                        DeleteOwn = true,
                        DeleteOthers = true,
                        ViewDrafts = true,
                        SaveDraft = true,
                        Submit = true,
                        ViewAllOrg = true,
                        ViewAllOrgs = true,
                        Export = true
                    },
                    Templates = new TemplatePermissions
                    {
                        View = true,
                        ViewBankTemplates = true,
                        CreateCustom = true,
                        EditCustom = true,
                        DeleteCustom = true,
                        ManageBankTemplates = true,
                        ShareAcrossOrgs = true
                    },
                    Drafts = new DraftPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true,
                        ViewOwn = true,
                        ViewOthers = true,
                        DeleteOwn = true,
                        DeleteOthers = true
                    },
                    Analytics = new AnalyticsPermissions
                    {
                        ViewOwnActivity = true,
                        ViewOrgActivity = true,
                        ViewAllActivity = true,
                        ExportReports = true
                    },
                    Settings = new SettingsPermissions
                    {
                        EditOrgSettings = true,
                        EditSystemSettings = true,
                        ManageIntegrations = true,
                        ViewLogs = true
                    }
                }
            },

            // ORG ADMIN (MANAGER)
            new PermissionTemplate
            {
                Role = "org_admin",
                DisplayName = "Organization Administrator (Manager)",
                Description = "Full access within own organization, can manage users and submit reports",
                IsSystemWide = false,
                Permissions = new PermissionSet
                {
                    Organizations = new OrganizationPermissions
                    {
                        ViewAll = false,
                        Create = false,
                        EditAny = false,
                        Delete = false,
                        ManageSettings = true
                    },
                    Users = new RoleBasedUserPermissions
                    {
                        ViewAllOrgs = false,
                        ViewOwnOrg = true,
                        Create = true,
                        EditAny = true,
                        DeleteAny = false,
                        ViewActivity = true,
                        ManageRoles = true
                    },
                    Reports = new ReportPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true,
                        DeleteOwn = true,
                        DeleteOthers = true,
                        ViewDrafts = true,
                        SaveDraft = true,
                        Submit = true, // SUBMIT = APPROVAL
                        ViewAllOrg = true,
                        ViewAllOrgs = false,
                        Export = true
                    },
                    Templates = new TemplatePermissions
                    {
                        View = true,
                        ViewBankTemplates = true,
                        CreateCustom = true,
                        EditCustom = true,
                        DeleteCustom = true,
                        ManageBankTemplates = false,
                        ShareAcrossOrgs = false
                    },
                    Drafts = new DraftPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true,
                        ViewOwn = true,
                        ViewOthers = true,
                        DeleteOwn = true,
                        DeleteOthers = true
                    },
                    Analytics = new AnalyticsPermissions
                    {
                        ViewOwnActivity = true,
                        ViewOrgActivity = true,
                        ViewAllActivity = false,
                        ExportReports = true
                    },
                    Settings = new SettingsPermissions
                    {
                        EditOrgSettings = true,
                        EditSystemSettings = false,
                        ManageIntegrations = true,
                        ViewLogs = true
                    }
                }
            },

            // EMPLOYEE
            new PermissionTemplate
            {
                Role = "employee",
                DisplayName = "Employee",
                Description = "Basic access - can create and edit reports, save drafts",
                IsSystemWide = false,
                Permissions = new PermissionSet
                {
                    Organizations = new OrganizationPermissions
                    {
                        ViewAll = false,
                        Create = false,
                        EditAny = false,
                        Delete = false,
                        ManageSettings = false
                    },
                    Users = new RoleBasedUserPermissions
                    {
                        ViewAllOrgs = false,
                        ViewOwnOrg = true,
                        Create = false,
                        EditAny = false,
                        DeleteAny = false,
                        ViewActivity = false,
                        ManageRoles = false
                    },
                    Reports = new ReportPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true, // Can edit any report in org
                        DeleteOwn = true,
                        DeleteOthers = false,
                        ViewDrafts = true,
                        SaveDraft = true,
                        Submit = false, // Cannot submit
                        ViewAllOrg = true,
                        ViewAllOrgs = false,
                        Export = true
                    },
                    Templates = new TemplatePermissions
                    {
                        View = true,
                        ViewBankTemplates = true,
                        CreateCustom = false,
                        EditCustom = false,
                        DeleteCustom = false,
                        ManageBankTemplates = false,
                        ShareAcrossOrgs = false
                    },
                    Drafts = new DraftPermissions
                    {
                        Create = true,
                        EditOwn = true,
                        EditOthers = true,
                        ViewOwn = true,
                        ViewOthers = true,
                        DeleteOwn = true,
                        DeleteOthers = false
                    },
                    Analytics = new AnalyticsPermissions
                    {
                        ViewOwnActivity = true,
                        ViewOrgActivity = false,
                        ViewAllActivity = false,
                        ExportReports = false
                    },
                    Settings = new SettingsPermissions
                    {
                        EditOrgSettings = false,
                        EditSystemSettings = false,
                        ManageIntegrations = false,
                        ViewLogs = false
                    }
                }
            }
        };

        await _permissionsCollection.InsertManyAsync(templates);
        
        // Create indexes
        await _permissionsCollection.Indexes.CreateOneAsync(
            new CreateIndexModel<PermissionTemplate>(
                Builders<PermissionTemplate>.IndexKeys.Ascending(pt => pt.Role),
                new CreateIndexOptions { Unique = true }
            )
        );

        _logger.LogInformation("✅ Seeded {Count} permission templates", templates.Count);
    }

    public async Task<bool> HasPermissionAsync(string userId, string permission)
    {
        // TODO: Implement permission checking logic
        // This will check user's role permissions + any permission overrides
        throw new NotImplementedException();
    }

    public async Task<PermissionSet> GetUserPermissionsAsync(string userId)
    {
        // TODO: Implement getting user's effective permissions
        throw new NotImplementedException();
    }
}
