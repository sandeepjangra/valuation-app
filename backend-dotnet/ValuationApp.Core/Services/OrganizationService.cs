using Microsoft.Extensions.Logging;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Common.Models;

namespace ValuationApp.Core.Services;

public class OrganizationService : IOrganizationService
{
    private readonly IOrganizationRepository _organizationRepository;
    private readonly ILogger<OrganizationService> _logger;

    public OrganizationService(
        IOrganizationRepository organizationRepository,
        ILogger<OrganizationService> logger)
    {
        _organizationRepository = organizationRepository;
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

        // Generate reference number in format: INITIALS-YYYYMMDD-####
        var referenceNumber = $"{organization.ReportReferenceInitials}-{DateTime.UtcNow:yyyyMMdd}-{organization.LastReferenceNumber:D4}";
        
        _logger.LogInformation("Generated reference number: {ReferenceNumber} for organization: {ShortName}", 
            referenceNumber, shortName);

        return referenceNumber;
    }

    public async Task<List<Organization>> GetAllActiveOrganizationsAsync()
    {
        _logger.LogInformation("Fetching all active organizations");
        return await _organizationRepository.GetAllActiveAsync();
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

        organization.UpdatedAt = DateTime.UtcNow;

        var updatedOrg = await _organizationRepository.UpdateAsync(organization);
        
        _logger.LogInformation("Organization updated successfully: {ShortName}", shortName);
        
        return updatedOrg;
    }
}
