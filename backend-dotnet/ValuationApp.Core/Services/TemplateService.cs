using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

public class TemplateService : ITemplateService
{
    private readonly ITemplateRepository _templateRepository;

    public TemplateService(ITemplateRepository templateRepository)
    {
        _templateRepository = templateRepository;
    }

    public async Task<Template?> GetTemplateAsync(string bankCode, string propertyType)
    {
        return await _templateRepository.GetTemplateByBankAndPropertyAsync(bankCode, propertyType);
    }

    public async Task<Template?> GetTemplateByIdAsync(string templateId)
    {
        return await _templateRepository.GetTemplateByIdAsync(templateId);
    }

    public async Task<List<Template>> GetTemplatesByBankCodeAsync(string bankCode)
    {
        return await _templateRepository.GetTemplatesByBankCodeAsync(bankCode);
    }

    public async Task<List<Template>> GetActiveTemplatesAsync()
    {
        return await _templateRepository.GetActiveTemplatesAsync();
    }
}
