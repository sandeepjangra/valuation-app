using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Interfaces;
using ValuationApp.Core.DTOs;

namespace ValuationApp.API.Controllers;

[ApiController]
[Route("api/org/{orgShortName}/custom-templates")]
public class CustomTemplatesController : ControllerBase
{
    private readonly ITemplateService _templateService;
    private readonly ICustomTemplateService _customTemplateService;
    private readonly ILogger<CustomTemplatesController> _logger;

    public CustomTemplatesController(
        ITemplateService templateService, 
        ICustomTemplateService customTemplateService,
        ILogger<CustomTemplatesController> logger)
    {
        _templateService = templateService;
        _customTemplateService = customTemplateService;
        _logger = logger;
    }

    /// <summary>
    /// Get template fields for custom template creation
    /// GET /api/org/{orgShortName}/custom-templates/fields?bank_code=SBI&property_type=land
    /// </summary>
    [HttpGet("fields")]
    public async Task<IActionResult> GetTemplateFields(
        [FromQuery(Name = "bank_code")] string bankCode,
        [FromQuery(Name = "property_type")] string propertyType)
    {
        try
        {
            _logger.LogInformation("🔥 CustomTemplates: Fetching fields for {BankCode}/{PropertyType}", bankCode, propertyType);
            
            if (string.IsNullOrEmpty(bankCode) || string.IsNullOrEmpty(propertyType))
            {
                return BadRequest(ApiResponse<object>.ErrorResponse("bank_code and property_type are required"));
            }

            // Use the same service as regular templates
            var aggregatedData = await _templateService.GetAggregatedTemplateAsync(bankCode, propertyType);
            
            if (aggregatedData == null)
            {
                _logger.LogWarning("Template not found for {BankCode}/{PropertyType}", bankCode, propertyType);
                return NotFound(ApiResponse<object>.ErrorResponse($"Template not found for {bankCode}/{propertyType}"));
            }

            _logger.LogInformation(
                "✅ Retrieved template for {BankCode}/{PropertyType}. Common fields: {CommonFieldsCount}, Tabs: {TabsCount}",
                bankCode, propertyType,
                aggregatedData.CommonFields.Fields.Count,
                aggregatedData.TemplateStructure.Tabs?.Count ?? 0
            );

            // Filter fields to only include those with includeInCustomTemplate = true
            var filteredCommonFields = FilterFieldsByCustomTemplate(aggregatedData.CommonFields.Fields);
            var filteredTabs = FilterTabsByCustomTemplate(aggregatedData.TemplateStructure.Tabs);

            _logger.LogInformation(
                "🔍 Filtered fields: Common {Filtered}/{Total}, Tabs: {TabCount}",
                filteredCommonFields.Count, aggregatedData.CommonFields.Fields.Count, filteredTabs.Count
            );

            // Transform filtered fields to frontend format
            var transformedCommonFields = TransformFieldsToFrontendFormat(filteredCommonFields);
            var transformedTabs = TransformTabsToFrontendFormat(filteredTabs);

            // Transform to frontend format (same as TemplatesController)
            var response = new
            {
                success = true,
                bankCode = bankCode,
                propertyType = propertyType,
                templateInfo = new
                {
                    templateId = aggregatedData.Template.TemplateId,
                    templateName = aggregatedData.Template.TemplateName,
                    propertyType = aggregatedData.Template.PropertyType,
                    bankCode = aggregatedData.Bank.BankCode,
                    bankName = aggregatedData.Bank.BankName,
                    version = aggregatedData.Template.Version
                },
                commonFields = transformedCommonFields,
                bankSpecificTabs = transformedTabs
            };
            
            _logger.LogInformation("✅ CustomTemplates: Successfully returned fields for {BankCode}/{PropertyType}", bankCode, propertyType);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error in CustomTemplates.GetTemplateFields: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse("Failed to retrieve template fields"));
        }
    }

    /// <summary>
    /// List all custom templates with optional filtering
    /// GET /api/custom-templates?bankCode=SBI&propertyType=land
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetTemplates(
        [FromQuery] string? bankCode,
        [FromQuery] string? propertyType)
    {
        try
        {
            _logger.LogInformation("📋 CustomTemplates: Listing templates (bankCode: {BankCode}, propertyType: {PropertyType})", 
                bankCode ?? "all", propertyType ?? "all");

            var templates = await _customTemplateService.ListCustomTemplatesAsync(bankCode, propertyType);

            _logger.LogInformation("✅ CustomTemplates: Found {Count} templates", templates.Count);

            var response = new
            {
                success = true,
                message = "Custom templates retrieved successfully",
                data = templates,
                count = new
                {
                    total = templates.Count,
                    filtered = templates.Count
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error listing custom templates: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse("Failed to retrieve custom templates"));
        }
    }

    /// <summary>
    /// Get a specific custom template by ID
    /// GET /api/custom-templates/{id}
    /// </summary>
    [HttpGet("{id}")]
    public async Task<IActionResult> GetTemplate(string id)
    {
        try
        {
            _logger.LogInformation("🔍 CustomTemplates: Getting template {TemplateId}", id);

            var template = await _customTemplateService.GetCustomTemplateByIdAsync(id);

            if (template == null)
            {
                _logger.LogWarning("⚠️ CustomTemplates: Template {TemplateId} not found", id);
                return NotFound(ApiResponse<object>.ErrorResponse($"Template {id} not found"));
            }

            _logger.LogInformation("✅ CustomTemplates: Successfully retrieved template {TemplateId}", id);

            return Ok(ApiResponse<SavedCustomTemplateDto>.SuccessResponse(
                template,
                "Custom template retrieved successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error getting custom template: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse("Failed to retrieve custom template"));
        }
    }

    /// <summary>
    /// Create a new custom template
    /// POST /api/custom-templates
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateTemplate([FromBody] CreateCustomTemplateRequest request)
    {
        try
        {
            _logger.LogInformation("➕ CustomTemplates: Creating new template '{TemplateName}' for {BankCode}/{PropertyType}", 
                request.TemplateName, request.BankCode, request.PropertyType);

            // Validate request
            if (string.IsNullOrWhiteSpace(request.TemplateName))
            {
                return BadRequest(ApiResponse<object>.ErrorResponse("Template name is required"));
            }

            if (string.IsNullOrWhiteSpace(request.BankCode))
            {
                return BadRequest(ApiResponse<object>.ErrorResponse("Bank code is required"));
            }

            if (string.IsNullOrWhiteSpace(request.PropertyType))
            {
                return BadRequest(ApiResponse<object>.ErrorResponse("Property type is required"));
            }

            // Create the template
            var template = await _customTemplateService.CreateCustomTemplateAsync(request);

            var response = new CustomTemplateCreateResponse
            {
                TemplateId = template.Id,
                Template = template
            };

            _logger.LogInformation("✅ CustomTemplates: Successfully created template with ID {TemplateId}", template.Id);

            return Ok(ApiResponse<CustomTemplateCreateResponse>.SuccessResponse(
                response,
                "Custom template created successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error creating custom template: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse($"Failed to create custom template: {ex.Message}"));
        }
    }

    /// <summary>
    /// Update an existing custom template
    /// PUT /api/custom-templates/{id}
    /// </summary>
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateTemplate(string id, [FromBody] UpdateCustomTemplateRequest request)
    {
        try
        {
            _logger.LogInformation("✏️ CustomTemplates: Updating template {TemplateId}", id);

            var template = await _customTemplateService.UpdateCustomTemplateAsync(id, request);

            _logger.LogInformation("✅ CustomTemplates: Successfully updated template {TemplateId}", id);

            return Ok(ApiResponse<SavedCustomTemplateDto>.SuccessResponse(
                template,
                "Custom template updated successfully"
            ));
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning("⚠️ CustomTemplates: Invalid template ID {TemplateId}", id);
            return BadRequest(ApiResponse<object>.ErrorResponse(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error updating custom template: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse($"Failed to update custom template: {ex.Message}"));
        }
    }

    /// <summary>
    /// Delete a custom template
    /// DELETE /api/custom-templates/{id}
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteTemplate(string id)
    {
        try
        {
            _logger.LogInformation("🗑️ CustomTemplates: Deleting template {TemplateId}", id);

            var deleted = await _customTemplateService.DeleteCustomTemplateAsync(id);

            if (!deleted)
            {
                _logger.LogWarning("⚠️ CustomTemplates: Template {TemplateId} not found for deletion", id);
                return NotFound(ApiResponse<object>.ErrorResponse($"Template {id} not found"));
            }

            _logger.LogInformation("✅ CustomTemplates: Successfully deleted template {TemplateId}", id);

            return Ok(ApiResponse<object>.SuccessResponse(
                new { message = "Template deleted successfully" },
                "Custom template deleted successfully"
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error deleting custom template: {Message}", ex.Message);
            return StatusCode(500, ApiResponse<object>.ErrorResponse("Failed to delete custom template"));
        }
    }

    /// <summary>
    /// Health check for custom templates API
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(new { status = "healthy", service = "custom-templates" });
    }

    /// <summary>
    /// Filter fields to only include those with includeInCustomTemplate = true
    /// Also marks them as active and editable for custom template usage
    /// </summary>
    private List<Core.DTOs.Field> FilterFieldsByCustomTemplate(List<Core.DTOs.Field> fields)
    {
        if (fields == null || fields.Count == 0)
            return new List<Core.DTOs.Field>();

        var filtered = new List<Core.DTOs.Field>();

        foreach (var field in fields)
        {
            // Check if field has includeInCustomTemplate = true
            if (field.IncludeInCustomTemplate == true)
            {
                // Mark field as active and editable for custom templates
                field.IsActive = true;
                field.IsReadonly = false;

                // If it's a group field, also filter its subFields
                if (field.FieldType == "group" && field.SubFields != null && field.SubFields.Count > 0)
                {
                    field.SubFields = FilterFieldsByCustomTemplate(field.SubFields);
                    // Only include the group if it has filtered subFields
                    if (field.SubFields.Count > 0)
                    {
                        filtered.Add(field);
                    }
                }
                else
                {
                    filtered.Add(field);
                }
            }
        }

        return filtered;
    }

    /// <summary>
    /// Filter tabs to only include sections/fields with includeInCustomTemplate = true
    /// </summary>
    private List<Core.DTOs.Tab> FilterTabsByCustomTemplate(List<Core.DTOs.Tab>? tabs)
    {
        if (tabs == null || tabs.Count == 0)
            return new List<Core.DTOs.Tab>();

        var filteredTabs = new List<Core.DTOs.Tab>();

        foreach (var tab in tabs)
        {
            var filteredTab = new Core.DTOs.Tab
            {
                TabId = tab.TabId,
                TabName = tab.TabName,
                SortOrder = tab.SortOrder,
                Description = tab.Description,
                HasSections = tab.HasSections,
                Fields = new List<Core.DTOs.Field>(), // Initialize empty fields array
                Sections = new List<Core.DTOs.Section>()
            };

            // Filter tab-level fields if any
            if (tab.Fields != null && tab.Fields.Count > 0)
            {
                filteredTab.Fields = FilterFieldsByCustomTemplate(tab.Fields);
            }

            if (tab.Sections != null && tab.Sections.Count > 0)
            {
                foreach (var section in tab.Sections)
                {
                    var filteredFields = FilterFieldsByCustomTemplate(section.Fields ?? new List<Core.DTOs.Field>());

                    // Only include section if it has filtered fields
                    if (filteredFields.Count > 0)
                    {
                        filteredTab.Sections.Add(new Core.DTOs.Section
                        {
                            SectionId = section.SectionId,
                            SectionName = section.SectionName,
                            SortOrder = section.SortOrder,
                            Description = section.Description,
                            Fields = filteredFields,
                            UseDocumentCollection = section.UseDocumentCollection,
                            OriginalFields = section.OriginalFields,
                            DocumentFilter = section.DocumentFilter
                        });
                    }
                }
            }

            // Only include tab if it has sections with fields OR has tab-level fields
            if (filteredTab.Sections.Count > 0 || filteredTab.Fields.Count > 0)
            {
                filteredTabs.Add(filteredTab);
            }
        }

        return filteredTabs;
    }

    /// <summary>
    /// Transform fields to frontend format with proper option handling
    /// </summary>
    private List<object> TransformFieldsToFrontendFormat(List<Core.DTOs.Field> fields)
    {
        return fields.Select(field => new
        {
            fieldId = field.FieldId,
            technicalName = field.TechnicalName,
            uiDisplayName = field.UiDisplayName,
            fieldType = field.FieldType,
            isRequired = field.IsRequired,
            isReadonly = field.IsReadonly ?? false,
            placeholder = field.Placeholder ?? "",
            helpText = field.HelpText ?? "",
            validation = field.Validation,
            gridSize = field.GridSize ?? 3,
            sortOrder = field.SortOrder ?? 0,
            isActive = field.IsActive,
            defaultValue = field.DefaultValue,
            includeInCustomTemplate = field.IncludeInCustomTemplate,
            options = TransformOptions(field.Options),
            subFields = field.SubFields != null && field.SubFields.Count > 0 
                ? TransformFieldsToFrontendFormat(field.SubFields) 
                : null
        }).ToList<object>();
    }

    /// <summary>
    /// Transform tabs to frontend format
    /// </summary>
    private List<object> TransformTabsToFrontendFormat(List<Core.DTOs.Tab> tabs)
    {
        return tabs.Select(tab => new
        {
            tabId = tab.TabId,
            tabName = tab.TabName,
            sortOrder = tab.SortOrder,
            description = tab.Description,
            hasSections = tab.HasSections,
            fields = tab.Fields != null ? TransformFieldsToFrontendFormat(tab.Fields) : new List<object>(),
            sections = tab.Sections != null 
                ? tab.Sections.Select(section => new
                {
                    sectionId = section.SectionId,
                    sectionName = section.SectionName,
                    sortOrder = section.SortOrder,
                    description = section.Description,
                    fields = section.Fields != null ? TransformFieldsToFrontendFormat(section.Fields) : new List<object>()
                }).ToList<object>()
                : new List<object>()
        }).ToList<object>();
    }

    /// <summary>
    /// Transform options to proper {value, label} format for dropdowns
    /// Copied from TemplatesController with full Newtonsoft.Json support
    /// </summary>
    private object? TransformOptions(object? options)
    {
        if (options == null)
            return null;

        try
        {
            // Log what we're receiving for debugging
            var optionsJson = Newtonsoft.Json.JsonConvert.SerializeObject(options);
            _logger.LogDebug("TransformOptions received: {OptionsJson}", optionsJson);

            // Handle Newtonsoft.Json JArray (from MongoDB deserialization)
            if (options is Newtonsoft.Json.Linq.JArray jArray)
            {
                var transformedOptions = new List<object>();

                foreach (var item in jArray)
                {
                    // Check if it's a JObject with value and label
                    if (item is Newtonsoft.Json.Linq.JObject jObj)
                    {
                        var value = jObj["value"]?.ToString();
                        var label = jObj["label"]?.ToString();
                        
                        if (!string.IsNullOrWhiteSpace(value) && !string.IsNullOrWhiteSpace(label))
                        {
                            transformedOptions.Add(new { value, label });
                        }
                    }
                    // Check if it's a simple string value
                    else if (item.Type == Newtonsoft.Json.Linq.JTokenType.String)
                    {
                        var str = item.ToString();
                        if (!string.IsNullOrWhiteSpace(str))
                        {
                            transformedOptions.Add(new { value = str, label = str });
                        }
                    }
                    // Check if it's a nested array (malformed structure like [[[]]]])
                    else if (item is Newtonsoft.Json.Linq.JArray nestedArray && nestedArray.Count >= 2)
                    {
                        // Try to extract value and label from nested structure
                        // Structure: [[value], [label]]
                        try
                        {
                            var valueToken = nestedArray[0];
                            var labelToken = nestedArray[1];
                            
                            string? value = null;
                            string? label = null;
                            
                            // Extract value (could be nested)
                            if (valueToken is Newtonsoft.Json.Linq.JArray valueArray && valueArray.Count > 0)
                            {
                                value = valueArray[0]?.ToString();
                            }
                            else
                            {
                                value = valueToken?.ToString();
                            }
                            
                            // Extract label (could be nested)
                            if (labelToken is Newtonsoft.Json.Linq.JArray labelArray && labelArray.Count > 0)
                            {
                                label = labelArray[0]?.ToString();
                            }
                            else
                            {
                                label = labelToken?.ToString();
                            }
                            
                            if (!string.IsNullOrWhiteSpace(value) && !string.IsNullOrWhiteSpace(label))
                            {
                                transformedOptions.Add(new { value, label });
                            }
                        }
                        catch
                        {
                            // Skip malformed nested arrays
                            continue;
                        }
                    }
                }

                return transformedOptions.Count > 0 ? transformedOptions : null;
            }

            // If options is already a proper array, return it
            if (options is List<object> || options is object[])
            {
                var optionsList = options as IEnumerable<object> ?? new List<object>();
                var transformedOptions = new List<object>();

                foreach (var option in optionsList)
                {
                    // If it's already a proper object with value and label, keep it
                    if (option is IDictionary<string, object> dict && 
                        dict.ContainsKey("value") && dict.ContainsKey("label"))
                    {
                        transformedOptions.Add(new { 
                            value = dict["value"]?.ToString() ?? "", 
                            label = dict["label"]?.ToString() ?? "" 
                        });
                    }
                    // If it's a string, convert to {value, label} format
                    else if (option is string str && !string.IsNullOrWhiteSpace(str))
                    {
                        transformedOptions.Add(new { value = str, label = str });
                    }
                }

                return transformedOptions.Count > 0 ? transformedOptions : null;
            }

            // If options is a string array
            if (options is string[] stringArray)
            {
                return stringArray.Where(s => !string.IsNullOrWhiteSpace(s))
                    .Select(s => new { value = s, label = s })
                    .ToList<object>();
            }

            _logger.LogWarning("TransformOptions: Unhandled options type: {OptionsType}", options.GetType().Name);
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error transforming options");
            return null;
        }
    }
}
