using System.Security.Claims;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.API.Middleware;

/// <summary>
/// Middleware to validate and inject organization context into HTTP requests
/// - Validates that the organization exists and is active
/// - Validates that the user has access to the organization (authorization)
/// - Sets organization database context for downstream services
/// </summary>
public class OrganizationContextMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<OrganizationContextMiddleware> _logger;

    public OrganizationContextMiddleware(
        RequestDelegate next,
        ILogger<OrganizationContextMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(
        HttpContext context, 
        IOrganizationService organizationService,
        IOrganizationDatabaseContext orgDatabaseContext)
    {
        var path = context.Request.Path.Value;

        // Skip organization validation for certain paths
        if (ShouldSkipValidation(path))
        {
            await _next(context);
            return;
        }

        // Extract orgShortName from route
        var orgShortName = context.Request.RouteValues["orgShortName"]?.ToString();

        if (string.IsNullOrEmpty(orgShortName))
        {
            _logger.LogWarning("No organization shortName found in route: {Path}", path);
            await _next(context);
            return;
        }

        _logger.LogInformation("Validating organization: {OrgShortName}", orgShortName);

        // Validate organization exists and is active
        var organization = await organizationService.GetByShortNameAsync(orgShortName);

        if (organization == null)
        {
            _logger.LogWarning("Organization not found: {OrgShortName}", orgShortName);
            context.Response.StatusCode = 404;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                success = false,
                message = $"Organization '{orgShortName}' not found",
                errors = new[] { "ORGANIZATION_NOT_FOUND" }
            });
            return;
        }

        if (!organization.IsActive)
        {
            _logger.LogWarning("Organization is inactive: {OrgShortName}", orgShortName);
            context.Response.StatusCode = 403;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                success = false,
                message = $"Organization '{orgShortName}' is inactive",
                errors = new[] { "ORGANIZATION_INACTIVE" }
            });
            return;
        }

        // ===== NEW: Authorization Check =====
        // Validate that the user has access to this organization
        if (!await ValidateUserAccessAsync(context, orgShortName))
        {
            return; // Response already written by ValidateUserAccessAsync
        }

        // ===== NEW: Set Organization Database Context =====
        // Get user claims
        var userOrgShortName = context.User.FindFirst("org_short_name")?.Value;
        var isSystemAdmin = userOrgShortName == "system-administration";

        // Set the organization database context for this request
        orgDatabaseContext.SetOrganizationContext(orgShortName, isSystemAdmin);

        // Add organization to HttpContext.Items for downstream use
        context.Items["Organization"] = organization;
        context.Items["OrganizationShortName"] = orgShortName;
        context.Items["OrganizationId"] = organization.OrganizationId;
        context.Items["IsSystemAdmin"] = isSystemAdmin;

        _logger.LogInformation("✅ Organization validated successfully: {OrgShortName} ({OrgId}) - SystemAdmin: {IsSystemAdmin}", 
            orgShortName, organization.OrganizationId, isSystemAdmin);

        await _next(context);
    }

    /// <summary>
    /// Validate that the authenticated user has access to the requested organization
    /// </summary>
    private async Task<bool> ValidateUserAccessAsync(HttpContext context, string requestedOrgShortName)
    {
        // Check if user is authenticated
        if (!context.User.Identity?.IsAuthenticated ?? true)
        {
            _logger.LogWarning("Unauthenticated user attempting to access organization: {OrgShortName}", requestedOrgShortName);
            context.Response.StatusCode = 401;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                success = false,
                message = "Authentication required",
                errors = new[] { "UNAUTHORIZED" }
            });
            return false;
        }

        // Get user's organization from JWT claims
        var userOrgShortName = context.User.FindFirst("org_short_name")?.Value;
        var isSystemAdminClaim = context.User.FindFirst("is_system_admin")?.Value;
        var userId = context.User.FindFirst("sub")?.Value;

        if (string.IsNullOrEmpty(userOrgShortName))
        {
            _logger.LogError("User {UserId} has no org_short_name claim in JWT token", userId);
            context.Response.StatusCode = 403;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                success = false,
                message = "Invalid user token - missing organization information",
                errors = new[] { "INVALID_TOKEN" }
            });
            return false;
        }

        // System administrators can access any organization
        var isSystemAdmin = userOrgShortName == "system-administration";
        
        if (isSystemAdmin)
        {
            _logger.LogInformation("✅ System admin {UserId} accessing organization: {OrgShortName}", 
                userId, requestedOrgShortName);
            return true;
        }

        // Regular users can ONLY access their own organization
        if (userOrgShortName != requestedOrgShortName)
        {
            _logger.LogWarning("🚫 User {UserId} from org '{UserOrg}' attempted to access org '{RequestedOrg}'", 
                userId, userOrgShortName, requestedOrgShortName);
            
            context.Response.StatusCode = 403;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new
            {
                success = false,
                message = $"Access denied. You do not have permission to access organization '{requestedOrgShortName}'",
                errors = new[] { "ORGANIZATION_ACCESS_DENIED" }
            });
            return false;
        }

        _logger.LogInformation("✅ User {UserId} authorized to access their organization: {OrgShortName}", 
            userId, requestedOrgShortName);
        return true;
    }

    private bool ShouldSkipValidation(string? path)
    {
        if (string.IsNullOrEmpty(path))
            return true;

        // Skip validation for these paths
        var skipPaths = new[]
        {
            "/health",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/swagger",
            "/api/banks", // Banks are shared resources, not org-specific
            "/api/templates", // Bank templates are shared resources
            "/api/organizations", // Organization management endpoints
            "/_framework",
            "/_content"
        };

        return skipPaths.Any(skip => path.StartsWith(skip, StringComparison.OrdinalIgnoreCase));
    }
}
