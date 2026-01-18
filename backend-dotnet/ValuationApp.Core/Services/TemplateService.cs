using System.Text.Json;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Interfaces;

namespace ValuationApp.Core.Services;

public class TemplateService : ITemplateService
{
    private readonly IBankRepository _bankRepository;
    private readonly ITemplateRepository _templateRepository;

    public TemplateService(IBankRepository bankRepository, ITemplateRepository templateRepository)
    {
        _bankRepository = bankRepository;
        _templateRepository = templateRepository;
    }

    public async Task<AggregatedTemplateResponse?> GetAggregatedTemplateAsync(string bankCode, string propertyType)
    {
        // 1. Get bank information
        var bank = await _bankRepository.GetBankByCodeAsync(bankCode);
        if (bank == null)
            return null;

        // 2. Find the template for this property type
        var template = bank.Templates?.FirstOrDefault(t => 
            t.PropertyType.Equals(propertyType, StringComparison.OrdinalIgnoreCase) && 
            t.IsActive);
        
        if (template == null)
            return null;

        // 3. Get template structure from collection
        var templateStructure = await _templateRepository.GetTemplateStructureAsync(template.CollectionRef ?? "");
        
        // 4. Get common fields
        var commonFieldsData = await _templateRepository.GetCommonFieldsAsync();
        
        // 5. Get applicable document types
        var documentTypes = await _templateRepository.GetDocumentTypesAsync(bankCode, propertyType);

        // 6. Build aggregated response
        var response = new AggregatedTemplateResponse
        {
            Bank = new BankInfo
            {
                BankId = bank.BankId,
                BankCode = bank.BankCode,
                BankName = bank.BankName,
                BankShortName = bank.BankShortName
            },
            Template = new TemplateInfo
            {
                TemplateId = template.TemplateId,
                TemplateCode = template.TemplateCode,
                TemplateName = template.TemplateName,
                PropertyType = template.PropertyType,
                CollectionRef = template.CollectionRef ?? "",
                Version = template.Version
            },
            TemplateStructure = ParseTemplateStructure(templateStructure),
            DocumentTypes = ParseDocumentTypes(documentTypes),
            CommonFields = ParseCommonFields(commonFieldsData)
        };

        return response;
    }

    private TemplateStructure ParseTemplateStructure(object? data)
    {
        if (data == null)
            return new TemplateStructure();

        try
        {
            var json = Newtonsoft.Json.JsonConvert.SerializeObject(data);
            var jObject = JObject.Parse(json);
            
            var structure = new TemplateStructure();

            // Parse metadata
            if (jObject["metadata"] != null)
            {
                structure.Metadata = jObject["metadata"].ToObject<TemplateMetadata>();
            }

            // Parse templateMetadata
            if (jObject["templateMetadata"] != null)
            {
                structure.TemplateMetadata = jObject["templateMetadata"].ToObject<TemplateMetadataDetails>();
                
                // Extract tabs from templateMetadata (these have section metadata but no fields)
                if (structure.TemplateMetadata?.Tabs != null)
                {
                    structure.Tabs = structure.TemplateMetadata.Tabs;
                    
                    // Now merge fields from documents array into the sections
                    if (jObject["documents"] is JArray documentsArray)
                    {
                        Console.WriteLine($"Found {documentsArray.Count} documents to merge");
                        
                        // Build a map of section ID to fields from documents
                        var sectionFieldsMap = new Dictionary<string, List<Field>>();
                        
                        foreach (var doc in documentsArray)
                        {
                            if (doc["sections"] is JArray sectionsArray)
                            {
                                foreach (var section in sectionsArray)
                                {
                                    var sectionId = section["sectionId"]?.ToString();
                                    if (!string.IsNullOrEmpty(sectionId))
                                    {
                                        if (section["fields"] is JArray fieldsArray && fieldsArray.Count > 0)
                                        {
                                            var fields = fieldsArray.ToObject<List<Field>>() ?? new List<Field>();
                                            
                                            if (!sectionFieldsMap.ContainsKey(sectionId))
                                            {
                                                sectionFieldsMap[sectionId] = new List<Field>();
                                            }
                                            sectionFieldsMap[sectionId].AddRange(fields);
                                            
                                            Console.WriteLine($"Loaded {fields.Count} fields for section {sectionId}");
                                        }
                                        
                                        // Extract document collection metadata
                                        if (section["useDocumentCollection"]?.ToObject<bool>() == true)
                                        {
                                            Console.WriteLine($"Section {sectionId} uses document collection");
                                            
                                            // Store metadata to be applied later
                                            if (!sectionFieldsMap.ContainsKey(sectionId))
                                            {
                                                sectionFieldsMap[sectionId] = new List<Field>();
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Build a metadata map for sections with document collection
                        var sectionMetadataMap = new Dictionary<string, (bool useDocumentCollection, List<string> originalFields, object? documentFilter)>();
                        
                        foreach (var doc in documentsArray)
                        {
                            if (doc["sections"] is JArray sectionsArray2)
                            {
                                foreach (var section in sectionsArray2)
                                {
                                    var sectionId = section["sectionId"]?.ToString();
                                    var useDocCol = section["useDocumentCollection"]?.ToObject<bool>() ?? false;
                                    
                                    if (!string.IsNullOrEmpty(sectionId) && useDocCol)
                                    {
                                        var originalFields = section["originalFields"]?.ToObject<List<string>>() ?? new List<string>();
                                        var documentFilter = section["documentFilter"]?.ToObject<object>();
                                        
                                        sectionMetadataMap[sectionId] = (useDocCol, originalFields, documentFilter);
                                        Console.WriteLine($"Section {sectionId}: useDocumentCollection={useDocCol}, originalFields count={originalFields.Count}");
                                    }
                                }
                            }
                        }
                        
                        // Now merge the fields into the tabs structure
                        foreach (var tab in structure.Tabs)
                        {
                            if (tab.Sections != null)
                            {
                                foreach (var section in tab.Sections)
                                {
                                    // Apply document collection metadata if available
                                    if (sectionMetadataMap.ContainsKey(section.SectionId))
                                    {
                                        var metadata = sectionMetadataMap[section.SectionId];
                                        section.UseDocumentCollection = metadata.useDocumentCollection;
                                        section.OriginalFields = metadata.originalFields;
                                        section.DocumentFilter = metadata.documentFilter;
                                        Console.WriteLine($"Applied document collection metadata to section {section.SectionId}");
                                    }
                                    
                                    if (sectionFieldsMap.ContainsKey(section.SectionId))
                                    {
                                        section.Fields = sectionFieldsMap[section.SectionId];
                                        Console.WriteLine($"Merged {section.Fields.Count} fields into tab '{tab.TabName}', section '{section.SectionName}'");
                                    }
                                    else
                                    {
                                        // Initialize empty list if no fields found
                                        section.Fields = new List<Field>();
                                        Console.WriteLine($"No fields found for section {section.SectionId}, initialized empty list");
                                    }
                                }
                            }
                        }
                        
                        // Handle tabs without sections (fields at tab level)
                        // Build a map of documentId to fields from documents array
                        var tabFieldsMap = new Dictionary<string, List<Field>>();
                        
                        foreach (var doc in documentsArray)
                        {
                            var documentId = doc["documentId"]?.ToString();
                            
                            // Check if this document has fields at the top level (no sections)
                            if (!string.IsNullOrEmpty(documentId) && doc["fields"] is JArray fieldsArray && fieldsArray.Count > 0)
                            {
                                var fields = fieldsArray.ToObject<List<Field>>() ?? new List<Field>();
                                
                                if (!tabFieldsMap.ContainsKey(documentId))
                                {
                                    tabFieldsMap[documentId] = new List<Field>();
                                }
                                tabFieldsMap[documentId].AddRange(fields);
                                
                                Console.WriteLine($"Loaded {fields.Count} fields for document/tab {documentId}");
                            }
                        }
                        
                        // Merge fields into tabs without sections
                        foreach (var tab in structure.Tabs)
                        {
                            // Only process tabs that don't have sections
                            if (tab.HasSections == false || tab.Sections == null || tab.Sections.Count == 0)
                            {
                                // Try to match by tabId or documentId from documents
                                if (tabFieldsMap.ContainsKey(tab.TabId))
                                {
                                    tab.Fields = tabFieldsMap[tab.TabId];
                                    Console.WriteLine($"Merged {tab.Fields.Count} fields into tab '{tab.TabName}' (no sections)");
                                }
                                else
                                {
                                    // Try alternative matches (e.g., inspection_checklist -> detailed_valuation)
                                    var matchingKey = tabFieldsMap.Keys.FirstOrDefault(k => 
                                        k.Contains(tab.TabId.Replace("_", "")) || 
                                        tab.TabId.Contains(k.Replace("_", "")));
                                    
                                    if (matchingKey != null)
                                    {
                                        tab.Fields = tabFieldsMap[matchingKey];
                                        Console.WriteLine($"Merged {tab.Fields.Count} fields into tab '{tab.TabName}' via fuzzy match with {matchingKey}");
                                    }
                                    else
                                    {
                                        // Initialize empty list if no fields found
                                        tab.Fields = tab.Fields ?? new List<Field>();
                                        Console.WriteLine($"No fields found for tab {tab.TabId}, initialized empty list");
                                    }
                                }
                            }
                        }
                        
                        Console.WriteLine("Field merging complete!");
                    }
                }
            }

            return structure;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error parsing template structure: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            return new TemplateStructure();
        }
    }

    private List<DocumentType> ParseDocumentTypes(List<object> data)
    {
        if (data == null || data.Count == 0)
            return new List<DocumentType>();

        try
        {
            var json = Newtonsoft.Json.JsonConvert.SerializeObject(data);
            return Newtonsoft.Json.JsonConvert.DeserializeObject<List<DocumentType>>(json) ?? new List<DocumentType>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error parsing document types: {ex.Message}");
            return new List<DocumentType>();
        }
    }

    private CommonFields ParseCommonFields(object? data)
    {
        if (data == null)
            return new CommonFields();

        try
        {
            // Use Newtonsoft.Json for better dynamic object handling
            var json = Newtonsoft.Json.JsonConvert.SerializeObject(data);
            var jObject = JObject.Parse(json);

            var commonFields = new CommonFields
            {
                CollectionName = jObject["collectionName"]?.ToString() ?? "",
                Description = jObject["description"]?.ToString() ?? "",
                Version = jObject["version"]?.ToString() ?? ""
            };

            // Parse fields array
            if (jObject["fields"] is JArray fieldsArray)
            {
                commonFields.Fields = fieldsArray.ToObject<List<Field>>() ?? new List<Field>();
            }

            return commonFields;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error parsing common fields: {ex.Message}");
            return new CommonFields();
        }
    }
}
