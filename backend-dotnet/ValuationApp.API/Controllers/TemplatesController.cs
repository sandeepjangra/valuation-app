using Microsoft.AspNetCore.Mvc;
using ValuationApp.Common.Models;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TemplatesController : ControllerBase
{
    private readonly ITemplateService _templateService;
    private readonly ILogger<TemplatesController> _logger;

    public TemplatesController(ITemplateService templateService, ILogger<TemplatesController> logger)
    {
        _templateService = templateService;
        _logger = logger;
    }

    /// <summary>
    /// Get aggregated template data including common fields, bank-specific fields, and document types
    /// </summary>
    /// <param name="bankCode">Bank code (e.g., SBI, PNB)</param>
    /// <param name="templateCode">Template code (e.g., land-property, apartment-property)</param>
    /// <returns>Aggregated template response with all fields and structure</returns>
    [HttpGet("{bankCode}/{templateCode}/aggregated-fields")]
    public async Task<IActionResult> GetAggregatedTemplateFields(string bankCode, string templateCode)
    {
        try
        {
            _logger.LogInformation("Fetching aggregated template for {BankCode}/{TemplateCode}", bankCode, templateCode);
            
            // Extract property type from template code (land-property -> land, apartment-property -> apartment)
            var propertyType = ExtractPropertyType(templateCode);
            
            if (string.IsNullOrEmpty(propertyType))
            {
                _logger.LogWarning("Invalid template code: {TemplateCode}", templateCode);
                return BadRequest(ApiResponse<object>.ErrorResponse(
                    $"Invalid template code: {templateCode}. Expected format: 'land-property' or 'apartment-property'"
                ));
            }

            var aggregatedData = await _templateService.GetAggregatedTemplateAsync(bankCode, propertyType);
            
            if (aggregatedData == null)
            {
                _logger.LogWarning("Template not found for {BankCode}/{PropertyType}", bankCode, propertyType);
                return NotFound(ApiResponse<object>.ErrorResponse(
                    $"Template not found for bank '{bankCode}' and property type '{propertyType}'"
                ));
            }

            _logger.LogInformation(
                "Successfully retrieved aggregated template for {BankCode}/{TemplateCode}. " +
                "Common fields: {CommonFieldsCount}, Tabs: {TabsCount}, Document types: {DocTypesCount}",
                bankCode, templateCode,
                aggregatedData.CommonFields.Fields.Count,
                aggregatedData.TemplateStructure.Tabs?.Count ?? 0,
                aggregatedData.DocumentTypes.Count
            );
            
            // Transform to frontend-expected format
            try
            {
                var response = TransformToFrontendFormat(aggregatedData);
                _logger.LogInformation("Successfully transformed response for {BankCode}/{TemplateCode}", bankCode, templateCode);
                return Ok(response);
            }
            catch (Exception transformEx)
            {
                _logger.LogError(transformEx, "Error transforming response for {BankCode}/{TemplateCode}: {Message}", 
                    bankCode, templateCode, transformEx.Message);
                throw;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving aggregated template for {BankCode}/{TemplateCode}: {Message}", 
                bankCode, templateCode, ex.Message);
            
            return StatusCode(500, ApiResponse<object>.ErrorResponse(
                "Failed to retrieve template data. Please try again later."
            ));
        }
    }

    /// <summary>
    /// Health check endpoint for templates API
    /// </summary>
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(ApiResponse<object>.SuccessResponse(
            new { status = "healthy", service = "templates" },
            "Templates API is running"
        ));
    }

    private string ExtractPropertyType(string templateCode)
    {
        // Handle formats: "land-property", "apartment-property", "land", "apartment"
        var lower = templateCode.ToLower();
        
        if (lower.Contains("land"))
            return "land";
        if (lower.Contains("apartment"))
            return "apartment";
        
        return string.Empty;
    }

    private object TransformToFrontendFormat(Core.DTOs.AggregatedTemplateResponse data)
    {
        // Transform to match frontend's AggregatedTemplateResponse interface
        return new
        {
            templateInfo = new
            {
                templateId = data.Template.TemplateId,
                templateName = data.Template.TemplateName,
                propertyType = data.Template.PropertyType,
                bankCode = data.Bank.BankCode,
                bankName = data.Bank.BankName,
                version = data.Template.Version
            },
            commonFields = TransformCommonFields(data.CommonFields.Fields),
            bankSpecificTabs = TransformBankSpecificTabs(data.TemplateStructure.Tabs, data.DocumentTypes),
            documentTypes = data.DocumentTypes,
            aggregatedAt = DateTime.UtcNow.ToString("o")
        };
    }

    private List<object> TransformCommonFields(List<Core.DTOs.Field> fields)
    {
        return fields.Where(f => f.IsActive).Select(field => new
        {
            _id = field.FieldId,
            fieldId = field.FieldId,
            technicalName = field.TechnicalName,
            uiDisplayName = field.UiDisplayName,
            fieldType = field.FieldType,
            isRequired = field.IsRequired,
            isReadonly = field.TechnicalName == "report_reference_number" || 
                         field.UiDisplayName.Contains("Reference") ||
                         field.FieldId.Contains("reference"),
            placeholder = field.Placeholder ?? "",
            helpText = field.HelpText ?? "",
            validation = field.Validation,
            // Tables should take full width (12 columns), other fields default to 3 columns
            gridSize = field.GridSize ?? (field.FieldType?.ToLower().Contains("table") == true ? 12 : 3),
            sortOrder = field.SortOrder ?? 0,
            isActive = field.IsActive,
            defaultValue = field.DefaultValue,
            options = TransformOptions(field.Options),
            tableConfig = TransformTableConfig(field.TableConfig),
            columns = TransformTableColumns(field.Columns),
            rows = TransformTableRows(field.Rows)
        }).ToList<object>();
    }

    private List<object> TransformBankSpecificTabs(List<Core.DTOs.Tab>? tabs, List<Core.DTOs.DocumentType> documentTypes)
    {
        if (tabs == null || tabs.Count == 0)
            return new List<object>();

        return tabs.Select(tab => new
        {
            tabId = tab.TabId,
            tabName = tab.TabName,
            sortOrder = tab.SortOrder,
            description = tab.Description,
            hasSections = tab.HasSections,
            sections = tab.Sections?.Select(section => new
            {
                sectionId = section.SectionId,
                sectionName = section.SectionName,
                sortOrder = section.SortOrder,
                description = section.Description,
                fields = ProcessSectionFields(section, documentTypes)
            }).ToList(),
            fields = new List<object>() // Bank-specific tabs typically have sections, not direct fields
        }).ToList<object>();
    }

    private List<object> ProcessSectionFields(Core.DTOs.Section section, List<Core.DTOs.DocumentType> documentTypes)
    {
        var fields = new List<object>();
        
        _logger.LogInformation(
            "Processing section {SectionId}: UseDocumentCollection={UseDoc}, OriginalFields count={OrigCount}, Regular fields count={FieldCount}",
            section.SectionId, 
            section.UseDocumentCollection ?? false,
            section.OriginalFields?.Count ?? 0,
            section.Fields?.Count ?? 0
        );
        
        // Check if this section uses document collection
        if (section.UseDocumentCollection == true && section.OriginalFields != null && section.OriginalFields.Count > 0)
        {
            _logger.LogInformation(
                "Section {SectionId} uses document collection. Filtering {Count} document types by originalFields: {Fields}",
                section.SectionId, documentTypes.Count, string.Join(", ", section.OriginalFields)
            );
            
            // Filter document types by originalFields and transform to field format
            foreach (var docType in documentTypes)
            {
                try
                {
                    _logger.LogDebug(
                        "Processing document type: {DocumentId}, checking against originalFields",
                        docType.DocumentId
                    );
                    
                    if (!string.IsNullOrEmpty(docType.DocumentId) && section.OriginalFields.Contains(docType.DocumentId))
                    {
                        _logger.LogInformation("Document {DocumentId} matches originalFields - adding to section", docType.DocumentId);
                        
                        fields.Add(new
                        {
                            fieldId = docType.DocumentId,
                            technicalName = docType.TechnicalName ?? docType.DocumentId,
                            uiDisplayName = docType.DocumentName ?? docType.DocumentId,
                            fieldType = docType.FieldType ?? "textarea",
                            isRequired = docType.IsRequired,
                            placeholder = docType.Description ?? "",
                            helpText = docType.HelpText ?? docType.Description ?? "",
                            validation = docType.Validation,
                            gridSize = 3, // Match standard field layout (4 fields per row)
                            sortOrder = docType.SortOrder,
                            isActive = docType.IsActive,
                            defaultValue = ""
                        });
                    }
                    else
                    {
                        _logger.LogDebug(
                            "Document {DocumentId} does NOT match originalFields: {OriginalFields}",
                            docType.DocumentId, string.Join(", ", section.OriginalFields)
                        );
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to process document type in section {SectionId}", section.SectionId);
                }
            }
            
            _logger.LogInformation(
                "Added {Count} document type fields to section {SectionId}",
                fields.Count, section.SectionId
            );
        }
        else
        {
            // Process regular fields
            if (section.Fields != null && section.Fields.Count > 0)
            {
                fields.AddRange(section.Fields.Select(field => new
                {
                    fieldId = field.FieldId,
                    technicalName = field.TechnicalName,
                    uiDisplayName = field.UiDisplayName,
                    fieldType = field.FieldType,
                    isRequired = field.IsRequired,
                    placeholder = field.Placeholder ?? "",
                    helpText = field.HelpText ?? "",
                    validation = field.Validation,
                    // Tables should take full width (12 columns), other fields default to 3 columns
                    gridSize = field.GridSize ?? (field.FieldType?.ToLower().Contains("table") == true ? 12 : 3),
                    sortOrder = field.SortOrder ?? 0,
                    isActive = true, // Default to true since MongoDB fields don't have isActive
                    defaultValue = field.DefaultValue,
                    options = TransformOptions(field.Options),
                    subFields = field.FieldType == "group" ? TransformSubFields(field) : null,
                    // Table-specific properties
                    tableConfig = TransformTableConfig(field.TableConfig),
                    columns = TransformTableColumns(field.Columns),
                    rows = TransformTableRows(field.Rows)
                }).ToList<object>());
            }
        }
        
        return fields;
    }

    private List<object>? TransformSubFields(Core.DTOs.Field field)
    {
        if (field.SubFields == null || field.SubFields.Count == 0)
            return null;

        return field.SubFields.Select(subField => new
        {
            fieldId = subField.FieldId,
            technicalName = subField.TechnicalName,
            uiDisplayName = subField.UiDisplayName,
            fieldType = subField.FieldType,
            isRequired = subField.IsRequired,
            placeholder = subField.Placeholder ?? "",
            helpText = subField.HelpText ?? "",
            validation = subField.Validation,
            gridSize = subField.GridSize ?? 12, // Sub-fields in groups default to full width for vertical stacking
            sortOrder = subField.SortOrder ?? 0,
            isActive = true,
            defaultValue = subField.DefaultValue,
            options = TransformOptions(subField.Options)
        }).ToList<object>();
    }

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

    private object? TransformTableColumns(object? columns)
    {
        if (columns == null)
            return null;

        try
        {
            _logger.LogDebug("TransformTableColumns received type: {Type}", columns.GetType().Name);
            
            // If it's already a deserialized list, convert back to JArray for processing
            if (columns is System.Collections.IEnumerable && !(columns is string))
            {
                var json = Newtonsoft.Json.JsonConvert.SerializeObject(columns);
                _logger.LogDebug("Converted to JSON: {Json}", json.Length > 200 ? json.Substring(0, 200) + "..." : json);
                columns = Newtonsoft.Json.JsonConvert.DeserializeObject<Newtonsoft.Json.Linq.JArray>(json);
            }
            
            if (columns is Newtonsoft.Json.Linq.JArray jArray)
            {
                _logger.LogDebug("Processing JArray with {Count} items", jArray.Count);
                var transformedColumns = new List<object>();

                foreach (var col in jArray)
                {
                    if (col is Newtonsoft.Json.Linq.JObject jObj)
                    {
                        var columnData = new Dictionary<string, object?>();
                        foreach (var prop in jObj.Properties())
                        {
                            // Extract first non-empty value from nested arrays
                            var value = ExtractFirstValue(prop.Value);
                            columnData[prop.Name] = value;
                            _logger.LogDebug("  Column property {Name} = {Value} (type: {Type})", 
                                prop.Name, value, value?.GetType().Name ?? "null");
                        }
                        if (columnData.Count > 0)
                        {
                            transformedColumns.Add(columnData);
                        }
                    }
                }

                _logger.LogDebug("Transformed {Count} columns", transformedColumns.Count);
                return transformedColumns.Count > 0 ? transformedColumns : null;
            }

            _logger.LogWarning("Columns is not JArray after conversion, returning as-is");
            return columns;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error transforming table columns");
            return null;
        }
    }

    private object? TransformTableRows(object? rows)
    {
        if (rows == null)
            return null;

        try
        {
            // Convert to JArray if it's a list
            if (rows is System.Collections.IEnumerable && !(rows is string))
            {
                var json = Newtonsoft.Json.JsonConvert.SerializeObject(rows);
                rows = Newtonsoft.Json.JsonConvert.DeserializeObject<Newtonsoft.Json.Linq.JArray>(json);
            }
            
            if (rows is Newtonsoft.Json.Linq.JArray jArray)
            {
                var transformedRows = new List<object>();

                foreach (var row in jArray)
                {
                    if (row is Newtonsoft.Json.Linq.JObject jObj)
                    {
                        var rowData = new Dictionary<string, object?>();
                        foreach (var prop in jObj.Properties())
                        {
                            var value = ExtractFirstValue(prop.Value);
                            rowData[prop.Name] = value;
                        }
                        if (rowData.Count > 0)
                        {
                            transformedRows.Add(rowData);
                        }
                    }
                }

                return transformedRows.Count > 0 ? transformedRows : null;
            }

            return rows;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error transforming table rows");
            return null;
        }
    }

    private object? TransformTableConfig(object? config)
    {
        if (config == null)
            return null;

        try
        {
            // Convert to JObject if it's a dictionary
            if (config is System.Collections.IDictionary || (config is System.Collections.IEnumerable && !(config is string)))
            {
                var json = Newtonsoft.Json.JsonConvert.SerializeObject(config);
                config = Newtonsoft.Json.JsonConvert.DeserializeObject<Newtonsoft.Json.Linq.JObject>(json);
            }
            
            if (config is Newtonsoft.Json.Linq.JObject jObj)
            {
                var configData = new Dictionary<string, object?>();
                foreach (var prop in jObj.Properties())
                {
                    var value = ExtractNestedValue(prop.Value);
                    configData[prop.Name] = value;
                }
                return configData.Count > 0 ? configData : null;
            }

            return config;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error transforming table config");
            return null;
        }
    }

    private object? ExtractFirstValue(Newtonsoft.Json.Linq.JToken token)
    {
        if (token == null)
            return null;

        // If it's a simple value, return it
        if (token.Type == Newtonsoft.Json.Linq.JTokenType.String ||
            token.Type == Newtonsoft.Json.Linq.JTokenType.Integer ||
            token.Type == Newtonsoft.Json.Linq.JTokenType.Float ||
            token.Type == Newtonsoft.Json.Linq.JTokenType.Boolean)
        {
            return token.ToObject<object>();
        }

        // If it's an array, get the first non-empty value
        if (token is Newtonsoft.Json.Linq.JArray arr && arr.Count > 0)
        {
            return ExtractFirstValue(arr[0]);
        }

        // If it's an object, try to extract meaningful data
        if (token is Newtonsoft.Json.Linq.JObject obj)
        {
            return obj.ToObject<Dictionary<string, object>>();
        }

        return token.ToString();
    }

    private object? ExtractNestedValue(Newtonsoft.Json.Linq.JToken token)
    {
        if (token == null)
            return null;

        // If it's a simple value, return it
        if (token.Type != Newtonsoft.Json.Linq.JTokenType.Array &&
            token.Type != Newtonsoft.Json.Linq.JTokenType.Object)
        {
            return token.ToObject<object>();
        }

        // If it's an array, recursively extract values
        if (token is Newtonsoft.Json.Linq.JArray arr)
        {
            var extracted = new List<object?>();
            foreach (var item in arr)
            {
                var value = ExtractNestedValue(item);
                if (value != null)
                {
                    extracted.Add(value);
                }
            }
            return extracted.Count > 0 ? extracted : null;
        }

        // If it's an object, convert to dictionary
        if (token is Newtonsoft.Json.Linq.JObject obj)
        {
            var dict = new Dictionary<string, object?>();
            foreach (var prop in obj.Properties())
            {
                dict[prop.Name] = ExtractNestedValue(prop.Value);
            }
            return dict.Count > 0 ? dict : null;
        }

        return null;
    }
}
