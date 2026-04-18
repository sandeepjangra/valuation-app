using Microsoft.Extensions.Logging;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Common.Models;

namespace ValuationApp.Core.Services;

public class OrganizationService : IOrganizationService
{
    private readonly IOrganizationRepository _organizationRepository;
    private readonly IOrganizationDatabaseService _organizationDatabaseService;
    private readonly ILogger<OrganizationService> _logger;

    public OrganizationService(
        IOrganizationRepository organizationRepository,
        IOrganizationDatabaseService organizationDatabaseService,
        ILogger<OrganizationService> logger)
    {
        _organizationRepository = organizationRepository;
        _organizationDatabaseService = organizationDatabaseService;
        _logger = logger;
    }

    public async Task<Organization?> GetByShortNameAsync(string shortName)
    {
        _logger.LogInformation("Fetching organization by short name: {ShortName}", shortName);
        return await _organizationRepository.GetByShortNameAsync(shortName);
    }

    public async Task<string> GetNextReferenceNumberAsync(string shortName)
    {
        _logger.LogInformation("Generating next reference number for organization: {ShortName}", shortName);

        var organization = await _organizationRepository.GetByShortNameAsync(shortName);
        
        if (organization == null)
        {
            _logger.LogError("Organization not found: {ShortName}", shortName);
            throw new InvalidOperationException($"Organization '{shortName}' not found");
        }

        if (string.IsNullOrEmpty(organization.ReportReferenceInitials))
        {
            _logger.LogError("Organization {ShortName} does not have Report Reference Initials configured", shortName);
            throw new InvalidOperationException(
                $"Organization '{shortName}' does not have Report Reference Initials configured. " +
                "Please contact your administrator to set the 'reportReferenceInitials' field.");
        }

        // Increment the reference number
        await _organizationRepository.IncrementReferenceNumberAsync(shortName);

        // Fetch the updated organization to get the new number
        organization = await _organizationRepository.GetByShortNameAsync(shortName);
        
        if (organization == null)
        {
            throw new InvalidOperationException($"Failed to fetch updated organization '{shortName}'");
        }

        // Generate reference number in format: {Initials}/ADMIN/999/{Increment}/{Date}
        // Example: CEV/ADMIN/999/0014/08022026
        var dateString = DateTime.UtcNow.ToString("ddMMyyyy");
        
        // Extract only the first part of initials if it contains slashes
        var initials = organization.ReportReferenceInitials ?? "ORG";
        if (initials.Contains('/'))
        {
            initials = initials.Split('/')[0];
        }
        
        var referenceNumber = $"{initials}/ADMIN/999/{organization.LastReferenceNumber:D4}/{dateString}";
        
        _logger.LogInformation("Generated reference number: {ReferenceNumber} for organization: {ShortName}", 
            referenceNumber, shortName);

        return referenceNumber;
    }

    public async Task<List<Organization>> GetAllActiveOrganizationsAsync()
    {
        _logger.LogInformation("Fetching all active organizations");
        return await _organizationRepository.GetAllActiveAsync();
    }

    public async Task<Organization?> CreateOrganizationAsync(CreateOrganizationRequest request)
    {
        _logger.LogInformation("Creating new organization: {OrganizationName}", request.Name);

        // Generate organization short name from the full name
        var orgShortName = GenerateShortName(request.Name);

        // Check if organization with this short name already exists
        var existingOrg = await _organizationRepository.GetByShortNameAsync(orgShortName);
        if (existingOrg != null)
        {
            _logger.LogWarning("Organization with short name {OrgShortName} already exists", orgShortName);
            throw new InvalidOperationException($"Organization with short name '{orgShortName}' already exists");
        }

        // Check if database already exists
        if (await _organizationDatabaseService.DatabaseExistsAsync(orgShortName))
        {
            _logger.LogWarning("Database for organization {OrgShortName} already exists", orgShortName);
            throw new InvalidOperationException($"Database for organization '{orgShortName}' already exists");
        }

        // Create new organization entity
        var organization = new Organization
        {
            OrganizationId = Guid.NewGuid().ToString(),
            ShortName = orgShortName,
            FullName = request.Name,
            Description = $"Organization: {request.Name}",
            ContactEmail = request.ContactEmail,
            ContactPhone = request.PhoneNumber ?? "",
            ReportReferenceInitials = request.ReportReferenceInitials ?? GenerateDefaultInitials(request.Name),
            LastReferenceNumber = 0,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        try
        {
            // 1. Save organization metadata to valuation_admin.organizations
            var createdOrg = await _organizationRepository.CreateAsync(organization);
            
            _logger.LogInformation("✅ Organization metadata saved: {OrgShortName}", orgShortName);

            // 2. Create dedicated MongoDB database for this organization
            var databaseCreated = await _organizationDatabaseService.CreateOrganizationDatabaseAsync(orgShortName);
            
            if (!databaseCreated)
            {
                _logger.LogError("Failed to create database for organization: {OrgShortName}", orgShortName);
                // Note: Organization metadata is already created. Consider rollback if needed.
                throw new InvalidOperationException($"Failed to create database for organization '{orgShortName}'");
            }

            _logger.LogInformation("✅ Organization created successfully with dedicated database: {OrgShortName}", orgShortName);
            
            return createdOrg;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create organization: {OrgShortName}", orgShortName);
            throw;
        }
    }

    private string GenerateShortName(string fullName)
    {
        // Remove special characters and convert to lowercase
        var shortName = fullName.ToLowerInvariant()
            .Replace(" ", "-")
            .Replace("_", "-")
            .Replace(".", "")
            .Replace(",", "")
            .Replace("'", "")
            .Replace("\"", "");
        
        // Remove any non-alphanumeric characters except hyphens
        shortName = new string(shortName.Where(c => char.IsLetterOrDigit(c) || c == '-').ToArray());
        
        // Ensure it doesn't start or end with hyphen
        shortName = shortName.Trim('-');
        
        return shortName;
    }

    private string GenerateDefaultInitials(string organizationName)
    {
        // Take first letter of each word, up to 3 letters
        var words = organizationName.Split(new[] { ' ', '-', '_' }, StringSplitOptions.RemoveEmptyEntries);
        var initials = string.Join("", words.Take(3).Select(w => w[0].ToString().ToUpper()));
        return initials;
    }

    public async Task<Organization?> UpdateOrganizationAsync(string shortName, UpdateOrganizationRequest request)
    {
        _logger.LogInformation("Updating organization: {ShortName}", shortName);

        var organization = await _organizationRepository.GetByShortNameAsync(shortName);
        
        if (organization == null)
        {
            _logger.LogWarning("Organization not found for update: {ShortName}", shortName);
            return null;
        }

        // Update only the fields that are provided (not null)
        if (request.FullName != null)
            organization.FullName = request.FullName;

        if (request.Description != null)
            organization.Description = request.Description;

        if (request.ContactEmail != null)
            organization.ContactEmail = request.ContactEmail;

        if (request.ContactPhone != null)
            organization.ContactPhone = request.ContactPhone;

        if (request.ReportReferenceInitials != null)
            organization.ReportReferenceInitials = request.ReportReferenceInitials;

        if (request.IsActive.HasValue)
            organization.IsActive = request.IsActive.Value;

        var updatedOrg = await _organizationRepository.UpdateAsync(organization);
        
        _logger.LogInformation("Organization updated successfully: {ShortName}", shortName);
        
        return updatedOrg;
    }
}
