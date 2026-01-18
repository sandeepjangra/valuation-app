using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Middleware;

/// <summary>
/// Middleware to validate and inject organization context into HTTP requests
/// Validates that the organization exists and is active before allowing request to proceed
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

    public async Task InvokeAsync(HttpContext context, IOrganizationService organizationService)
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

        // Add organization to HttpContext.Items for downstream use
        context.Items["Organization"] = organization;
        context.Items["OrganizationShortName"] = orgShortName;
        context.Items["OrganizationId"] = organization.Id;

        _logger.LogInformation("Organization validated successfully: {OrgShortName} ({OrgId})", 
            orgShortName, organization.Id);

        await _next(context);
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
