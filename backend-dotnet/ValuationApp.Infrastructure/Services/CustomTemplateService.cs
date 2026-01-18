using MongoDB.Bson;
using MongoDB.Driver;
using ValuationApp.Core.DTOs;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Services;

/// <summary>
/// Service implementation for custom templates
/// </summary>
public class CustomTemplateService : ICustomTemplateService
{
    private readonly IMongoDatabase _sharedResourcesDb;
    private readonly IMongoDatabase _systemAdminDb;
    private readonly MongoDbContext _context;

    public CustomTemplateService(MongoDbContext context)
    {
        _context = context;
        
        // Access shared_resources for template loading
        _sharedResourcesDb = _context.Client.GetDatabase("shared_resources");
        
        // Access system_administrator for storing custom templates
        _systemAdminDb = _context.Client.GetDatabase("system_administrator");
    }

    /// <summary>
    /// Load template fields that can have custom defaults
    /// Filters based on includeInCustomTemplate flag
    /// </summary>
    public async Task<CustomTemplateFieldsDto> LoadTemplateFieldsAsync(string bankCode, string propertyType)
    {
        var collectionName = $"{bankCode.ToLower()}_{propertyType.ToLower()}_property_details";
        Console.WriteLine($"[CustomTemplateService] Loading from collection: {collectionName}");
        
        var collection = _sharedResourcesDb.GetCollection<BsonDocument>(collectionName);

        var filter = Builders<BsonDocument>.Filter.Empty;
        var templateDoc = await collection.Find(filter).FirstOrDefaultAsync();

        if (templateDoc == null)
        {
            Console.WriteLine($"[CustomTemplateService] ERROR: Template not found in collection {collectionName}");
            throw new Exception($"Template not found for {bankCode} - {propertyType}");
        }
        
        Console.WriteLine($"[CustomTemplateService] Template document found, has {templateDoc.ElementCount} top-level fields");

        Console.WriteLine($"[CustomTemplateService] Template document found, has {templateDoc.ElementCount} top-level fields");

        var result = new CustomTemplateFieldsDto
        {
            BankCode = bankCode,
            PropertyType = propertyType,
            TemplateName = templateDoc.GetValue("templateName", new BsonString("")).AsString
        };

        // Parse documents array
        if (templateDoc.Contains("documents") && templateDoc["documents"].IsBsonArray)
        {
            var documentsArray = templateDoc["documents"].AsBsonArray;
            Console.WriteLine($"[CustomTemplateService] Found {documentsArray.Count} documents in template");

            foreach (var doc in documentsArray)
            {
                if (doc.IsBsonDocument)
                {
                    var docBson = doc.AsBsonDocument;
                    var customDoc = new CustomTemplateDocument
                    {
                        DocumentId = docBson.GetValue("documentId", new BsonString("")).AsString,
                        DocumentName = docBson.GetValue("documentName", new BsonString("")).AsString,
                        UiName = docBson.GetValue("uiName", new BsonString("")).AsString
                    };

                    // Parse sections
                    if (docBson.Contains("sections") && docBson["sections"].IsBsonArray)
                    {
                        var sectionsArray = docBson["sections"].AsBsonArray;

                        foreach (var section in sectionsArray)
                        {
                            if (section.IsBsonDocument)
                            {
                                var sectionBson = section.AsBsonDocument;
                                var customSection = new CustomTemplateSection
                                {
                                    SectionId = sectionBson.GetValue("sectionId", new BsonString("")).AsString,
                                    SectionName = sectionBson.GetValue("sectionName", new BsonString("")).AsString,
                                    SortOrder = sectionBson.GetValue("sortOrder", new BsonInt32(0)).AsInt32
                                };

                                // Parse fields in section
                                if (sectionBson.Contains("fields") && sectionBson["fields"].IsBsonArray)
                                {
                                    var fieldsArray = sectionBson["fields"].AsBsonArray;
                                    customSection.Fields = ParseFields(fieldsArray);
                                }

                                // Only add section if it has fields to customize
                                if (customSection.Fields.Any())
                                {
                                    customDoc.Sections.Add(customSection);
                                }
                            }
                        }
                    }

                    // Only add document if it has sections with fields
                    if (customDoc.Sections.Any())
                    {
                        result.Documents.Add(customDoc);
                    }
                }
            }
        }

        result.TemplateId = $"{bankCode}_{propertyType}_CUSTOM_TEMPLATE";
        return result;
    }

    /// <summary>
    /// Parse fields array and filter by includeInCustomTemplate
    /// </summary>
    private List<CustomTemplateField> ParseFields(BsonArray fieldsArray)
    {
        var fields = new List<CustomTemplateField>();

        foreach (var field in fieldsArray)
        {
            if (field.IsBsonDocument)
            {
                var fieldBson = field.AsBsonDocument;
                
                // Check if field should be included in custom template
                var includeInCustomTemplate = fieldBson.GetValue("includeInCustomTemplate", BsonBoolean.False).AsBoolean;

                if (includeInCustomTemplate)
                {
                    var customField = new CustomTemplateField
                    {
                        FieldId = fieldBson.GetValue("fieldId", new BsonString("")).AsString,
                        UiDisplayName = fieldBson.GetValue("uiDisplayName", new BsonString("")).AsString,
                        FieldType = fieldBson.GetValue("fieldType", new BsonString("text")).AsString,
                        HelpText = fieldBson.Contains("helpText") ? fieldBson["helpText"].AsString : null,
                        Placeholder = fieldBson.Contains("placeholder") ? fieldBson["placeholder"].AsString : null,
                        DefaultValue = fieldBson.Contains("defaultValue") ? fieldBson["defaultValue"].ToString() : null,
                        SortOrder = fieldBson.GetValue("sortOrder", new BsonInt32(0)).AsInt32,
                        IsGroup = fieldBson.GetValue("fieldType", new BsonString("")).AsString == "group"
                    };

                    // Handle group fields - check if group itself or subfields have includeInCustomTemplate
                    if (customField.IsGroup && fieldBson.Contains("subFields") && fieldBson["subFields"].IsBsonArray)
                    {
                        var subFieldsArray = fieldBson["subFields"].AsBsonArray;
                        customField.SubFields = ParseFields(subFieldsArray);
                        
                        // Only include group if it has subfields or if it's marked for inclusion
                        if (!customField.SubFields.Any())
                        {
                            continue; // Skip this group
                        }
                    }

                    // Parse options for select fields
                    if (customField.FieldType == "select" && fieldBson.Contains("options") && fieldBson["options"].IsBsonArray)
                    {
                        customField.Options = new List<FieldOption>();
                        var optionsArray = fieldBson["options"].AsBsonArray;
                        foreach (var option in optionsArray)
                        {
                            if (option.IsBsonDocument)
                            {
                                var optionBson = option.AsBsonDocument;
                                customField.Options.Add(new FieldOption
                                {
                                    Value = optionBson.GetValue("value", new BsonString("")).AsString,
                                    Label = optionBson.GetValue("label", new BsonString("")).AsString
                                });
                            }
                        }
                    }

                    fields.Add(customField);
                }
            }
        }

        return fields;
    }

    /// <summary>
    /// Get existing custom template for organization
    /// </summary>
    public async Task<CustomTemplateDto?> GetCustomTemplateAsync(string organizationId, string bankCode, string propertyType)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");
        
        var filter = Builders<BsonDocument>.Filter.And(
            Builders<BsonDocument>.Filter.Eq("organizationId", organizationId),
            Builders<BsonDocument>.Filter.Eq("bankCode", bankCode),
            Builders<BsonDocument>.Filter.Eq("propertyType", propertyType),
            Builders<BsonDocument>.Filter.Eq("isActive", true)
        );

        var doc = await collection.Find(filter).FirstOrDefaultAsync();
        
        if (doc == null) return null;

        return ParseCustomTemplateDocument(doc);
    }

    /// <summary>
    /// Save or update custom template
    /// </summary>
    public async Task<CustomTemplateDto> SaveCustomTemplateAsync(SaveCustomTemplateRequest request, string userId)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        var now = DateTime.UtcNow;
        BsonDocument doc;

        if (!string.IsNullOrEmpty(request.Id))
        {
            // Update existing
            var filter = Builders<BsonDocument>.Filter.And(
                Builders<BsonDocument>.Filter.Eq("_id", ObjectId.Parse(request.Id)),
                Builders<BsonDocument>.Filter.Eq("organizationId", request.OrganizationId)
            );

            var update = Builders<BsonDocument>.Update
                .Set("customDefaults", BsonArray.Create(request.CustomDefaults.Select(cd => cd.ToBsonDocument())))
                .Set("updatedAt", now);

            var options = new FindOneAndUpdateOptions<BsonDocument>
            {
                ReturnDocument = ReturnDocument.After
            };

            doc = await collection.FindOneAndUpdateAsync(filter, update, options);
            
            if (doc == null)
            {
                throw new Exception("Custom template not found or access denied");
            }
        }
        else
        {
            // Create new
            var templateId = $"{request.BankCode}_{request.PropertyType}_CUSTOM_TEMPLATE";
            
            doc = new BsonDocument
            {
                { "organizationId", request.OrganizationId },
                { "bankCode", request.BankCode },
                { "propertyType", request.PropertyType },
                { "templateId", templateId },
                { "templateName", $"{request.BankCode} {request.PropertyType} Custom Template" },
                { "customDefaults", BsonArray.Create(request.CustomDefaults.Select(cd => cd.ToBsonDocument())) },
                { "createdBy", userId },
                { "createdAt", now },
                { "updatedAt", now },
                { "isActive", true }
            };

            await collection.InsertOneAsync(doc);
        }

        return ParseCustomTemplateDocument(doc);
    }

    /// <summary>
    /// Delete custom template (soft delete)
    /// </summary>
    public async Task<bool> DeleteCustomTemplateAsync(string id, string organizationId)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");
        
        var filter = Builders<BsonDocument>.Filter.And(
            Builders<BsonDocument>.Filter.Eq("_id", ObjectId.Parse(id)),
            Builders<BsonDocument>.Filter.Eq("organizationId", organizationId)
        );

        var update = Builders<BsonDocument>.Update.Set("isActive", false);
        var result = await collection.UpdateOneAsync(filter, update);

        return result.ModifiedCount > 0;
    }

    /// <summary>
    /// Get all custom templates for organization
    /// </summary>
    public async Task<List<CustomTemplateDto>> GetOrganizationCustomTemplatesAsync(string organizationId)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");
        
        var filter = Builders<BsonDocument>.Filter.And(
            Builders<BsonDocument>.Filter.Eq("organizationId", organizationId),
            Builders<BsonDocument>.Filter.Eq("isActive", true)
        );

        var docs = await collection.Find(filter).ToListAsync();
        
        return docs.Select(ParseCustomTemplateDocument).ToList();
    }

    /// <summary>
    /// Parse BsonDocument to CustomTemplateDto
    /// </summary>
    private CustomTemplateDto ParseCustomTemplateDocument(BsonDocument doc)
    {
        var customDefaults = new List<CustomFieldDefault>();
        
        if (doc.Contains("customDefaults") && doc["customDefaults"].IsBsonArray)
        {
            var defaultsArray = doc["customDefaults"].AsBsonArray;
            foreach (var item in defaultsArray)
            {
                if (item.IsBsonDocument)
                {
                    var itemDoc = item.AsBsonDocument;
                    customDefaults.Add(new CustomFieldDefault
                    {
                        FieldId = itemDoc.GetValue("fieldId", new BsonString("")).AsString,
                        FieldPath = itemDoc.GetValue("fieldPath", new BsonString("")).AsString,
                        UiDisplayName = itemDoc.GetValue("uiDisplayName", new BsonString("")).AsString,
                        FieldType = itemDoc.GetValue("fieldType", new BsonString("")).AsString,
                        DefaultValue = itemDoc.Contains("defaultValue") ? itemDoc["defaultValue"].ToString() : null,
                        HelpText = itemDoc.Contains("helpText") ? itemDoc["helpText"].AsString : null,
                        SortOrder = itemDoc.GetValue("sortOrder", new BsonInt32(0)).AsInt32,
                        DocumentId = itemDoc.GetValue("documentId", new BsonString("")).AsString,
                        SectionId = itemDoc.GetValue("sectionId", new BsonString("")).AsString
                    });
                }
            }
        }

        return new CustomTemplateDto
        {
            Id = doc["_id"].ToString(),
            OrganizationId = doc.GetValue("organizationId", new BsonString("")).AsString,
            BankCode = doc.GetValue("bankCode", new BsonString("")).AsString,
            PropertyType = doc.GetValue("propertyType", new BsonString("")).AsString,
            TemplateId = doc.GetValue("templateId", new BsonString("")).AsString,
            TemplateName = doc.GetValue("templateName", new BsonString("")).AsString,
            CustomDefaults = customDefaults,
            CreatedBy = doc.GetValue("createdBy", new BsonString("")).AsString,
            CreatedAt = doc.GetValue("createdAt", new BsonDateTime(DateTime.UtcNow)).ToUniversalTime(),
            UpdatedAt = doc.GetValue("updatedAt", new BsonDateTime(DateTime.UtcNow)).ToUniversalTime(),
            IsActive = doc.GetValue("isActive", BsonBoolean.True).AsBoolean
        };
    }

    // ============================================
    // NEW METHODS FOR CUSTOM TEMPLATE CRUD
    // ============================================

    /// <summary>
    /// Create a new custom template in system_administrator.custom_templates collection
    /// </summary>
    public async Task<SavedCustomTemplateDto> CreateCustomTemplateAsync(CreateCustomTemplateRequest request)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        // TODO: Get actual user info from JWT token when auth is implemented
        // For now, using dummy values
        var userId = "dummy_user_id";
        var userName = "System Admin";

        // TODO: Validate organization context from JWT token
        // For now, get system-administration organization from database
        var organizationId = await GetSystemAdministrationOrgIdAsync();

        // Get bank name from bank code
        var bankName = await GetBankNameAsync(request.BankCode);

        var document = new BsonDocument
        {
            { "templateName", request.TemplateName },
            { "description", string.IsNullOrEmpty(request.Description) ? BsonNull.Value : (BsonValue)request.Description },
            { "bankCode", request.BankCode },
            { "bankName", bankName },
            { "propertyType", request.PropertyType },
            { "fieldValues", ConvertDictionaryToBson(request.FieldValues) },
            { "createdBy", userId },
            { "createdByName", userName },
            { "organizationId", organizationId },
            { "isActive", true },
            { "version", 1 },
            { "createdAt", DateTime.UtcNow },
            { "updatedAt", DateTime.UtcNow }
        };

        await collection.InsertOneAsync(document);

        // Return the created template
        return new SavedCustomTemplateDto
        {
            Id = document["_id"].ToString()!,
            TemplateName = request.TemplateName,
            Description = request.Description,
            BankCode = request.BankCode,
            BankName = bankName,
            PropertyType = request.PropertyType,
            FieldValues = request.FieldValues,
            CreatedBy = userId,
            CreatedByName = userName,
            OrganizationId = organizationId,
            IsActive = true,
            Version = 1,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
    }

    /// <summary>
    /// Get custom template by ID
    /// </summary>
    public async Task<SavedCustomTemplateDto?> GetCustomTemplateByIdAsync(string templateId)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        if (!ObjectId.TryParse(templateId, out var objectId))
        {
            return null;
        }

        var filter = Builders<BsonDocument>.Filter.Eq("_id", objectId);
        var document = await collection.Find(filter).FirstOrDefaultAsync();

        if (document == null)
        {
            return null;
        }

        return ParseSavedCustomTemplate(document);
    }

    /// <summary>
    /// Update an existing custom template
    /// </summary>
    public async Task<SavedCustomTemplateDto> UpdateCustomTemplateAsync(string templateId, UpdateCustomTemplateRequest request)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        if (!ObjectId.TryParse(templateId, out var objectId))
        {
            throw new ArgumentException("Invalid template ID format");
        }

        var filter = Builders<BsonDocument>.Filter.Eq("_id", objectId);
        var updateBuilder = Builders<BsonDocument>.Update;
        var updates = new List<UpdateDefinition<BsonDocument>>
        {
            updateBuilder.Set("updatedAt", DateTime.UtcNow)
        };

        if (!string.IsNullOrEmpty(request.TemplateName))
        {
            updates.Add(updateBuilder.Set("templateName", request.TemplateName));
        }

        if (request.Description != null)
        {
            updates.Add(updateBuilder.Set("description", request.Description));
        }

        if (request.FieldValues != null)
        {
            updates.Add(updateBuilder.Set("fieldValues", ConvertDictionaryToBson(request.FieldValues)));
        }

        var update = updateBuilder.Combine(updates);
        var result = await collection.FindOneAndUpdateAsync(
            filter,
            update,
            new FindOneAndUpdateOptions<BsonDocument>
            {
                ReturnDocument = ReturnDocument.After
            }
        );

        if (result == null)
        {
            throw new Exception($"Template with ID {templateId} not found");
        }

        return ParseSavedCustomTemplate(result);
    }

    /// <summary>
    /// Delete a custom template (soft delete by setting isActive = false)
    /// </summary>
    public async Task<bool> DeleteCustomTemplateAsync(string templateId)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        if (!ObjectId.TryParse(templateId, out var objectId))
        {
            return false;
        }

        var filter = Builders<BsonDocument>.Filter.Eq("_id", objectId);
        var update = Builders<BsonDocument>.Update
            .Set("isActive", false)
            .Set("updatedAt", DateTime.UtcNow);

        var result = await collection.UpdateOneAsync(filter, update);
        return result.ModifiedCount > 0;
    }

    /// <summary>
    /// List all custom templates with optional filtering
    /// </summary>
    public async Task<List<CustomTemplateListItemDto>> ListCustomTemplatesAsync(string? bankCode = null, string? propertyType = null)
    {
        var collection = _systemAdminDb.GetCollection<BsonDocument>("custom_templates");

        var filterBuilder = Builders<BsonDocument>.Filter;
        var filters = new List<FilterDefinition<BsonDocument>>
        {
            filterBuilder.Eq("isActive", true)
        };

        if (!string.IsNullOrEmpty(bankCode))
        {
            filters.Add(filterBuilder.Eq("bankCode", bankCode));
        }

        if (!string.IsNullOrEmpty(propertyType))
        {
            filters.Add(filterBuilder.Eq("propertyType", propertyType));
        }

        var filter = filterBuilder.And(filters);
        var documents = await collection.Find(filter).ToListAsync();

        return documents.Select(doc => new CustomTemplateListItemDto
        {
            Id = doc["_id"].ToString()!,
            TemplateName = doc.GetValue("templateName", "").AsString,
            Description = doc.Contains("description") && doc["description"] != BsonNull.Value 
                ? doc["description"].AsString 
                : null,
            BankCode = doc.GetValue("bankCode", "").AsString,
            BankName = doc.GetValue("bankName", "").AsString,
            PropertyType = doc.GetValue("propertyType", "").AsString,
            CreatedBy = doc.GetValue("createdBy", "").AsString,
            CreatedByName = doc.GetValue("createdByName", "").AsString,
            CreatedAt = doc.GetValue("createdAt", DateTime.UtcNow).ToUniversalTime(),
            UpdatedAt = doc.GetValue("updatedAt", DateTime.UtcNow).ToUniversalTime()
        }).ToList();
    }

    /// <summary>
    /// Get bank name from bankCode by querying the Banks collection
    /// </summary>
    public async Task<string> GetBankNameAsync(string bankCode)
    {
        try
        {
            var collection = _sharedResourcesDb.GetCollection<BsonDocument>("Banks");
            var filter = Builders<BsonDocument>.Filter.Eq("bank_code", bankCode);
            var bank = await collection.Find(filter).FirstOrDefaultAsync();

            if (bank != null && bank.Contains("bank_name"))
            {
                return bank["bank_name"].AsString;
            }

            // Fallback if not found
            return bankCode;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[CustomTemplateService] Error getting bank name: {ex.Message}");
            return bankCode;
        }
    }

    // ============================================
    // HELPER METHODS
    // ============================================

    /// <summary>
    /// Get system-administration organization ID from valuation_admin.organizations
    /// TODO: Replace with JWT token validation once auth is implemented
    /// </summary>
    private async Task<string> GetSystemAdministrationOrgIdAsync()
    {
        try
        {
            var adminDb = _context.Client.GetDatabase("valuation_admin");
            var collection = adminDb.GetCollection<BsonDocument>("organizations");
            var filter = Builders<BsonDocument>.Filter.Eq("shortName", "system-administration");
            var org = await collection.Find(filter).FirstOrDefaultAsync();

            if (org != null && org.Contains("_id"))
            {
                return org["_id"].ToString()!;
            }

            throw new Exception("System administration organization not found");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[CustomTemplateService] Error getting organization ID: {ex.Message}");
            throw;
        }
    }

    /// <summary>
    /// Convert Dictionary to BsonDocument for MongoDB storage
    /// </summary>
    private BsonDocument ConvertDictionaryToBson(Dictionary<string, object?> dictionary)
    {
        var bsonDoc = new BsonDocument();
        foreach (var kvp in dictionary)
        {
            if (kvp.Value == null)
            {
                bsonDoc[kvp.Key] = BsonNull.Value;
            }
            else if (kvp.Value is string str)
            {
                bsonDoc[kvp.Key] = str;
            }
            else if (kvp.Value is int intVal)
            {
                bsonDoc[kvp.Key] = intVal;
            }
            else if (kvp.Value is double dblVal)
            {
                bsonDoc[kvp.Key] = dblVal;
            }
            else if (kvp.Value is bool boolVal)
            {
                bsonDoc[kvp.Key] = boolVal;
            }
            else if (kvp.Value is DateTime dateVal)
            {
                bsonDoc[kvp.Key] = dateVal;
            }
            else
            {
                // For complex objects, convert to JSON string
                bsonDoc[kvp.Key] = kvp.Value.ToString() ?? "";
            }
        }
        return bsonDoc;
    }

    /// <summary>
    /// Parse BsonDocument to SavedCustomTemplateDto
    /// </summary>
    private SavedCustomTemplateDto ParseSavedCustomTemplate(BsonDocument doc)
    {
        var fieldValues = new Dictionary<string, object?>();
        if (doc.Contains("fieldValues") && doc["fieldValues"].IsBsonDocument)
        {
            var fieldValuesDoc = doc["fieldValues"].AsBsonDocument;
            foreach (var element in fieldValuesDoc.Elements)
            {
                fieldValues[element.Name] = element.Value.ToString();
            }
        }

        return new SavedCustomTemplateDto
        {
            Id = doc["_id"].ToString()!,
            TemplateName = doc.GetValue("templateName", "").AsString,
            Description = doc.Contains("description") && doc["description"] != BsonNull.Value 
                ? doc["description"].AsString 
                : null,
            BankCode = doc.GetValue("bankCode", "").AsString,
            BankName = doc.GetValue("bankName", "").AsString,
            PropertyType = doc.GetValue("propertyType", "").AsString,
            FieldValues = fieldValues,
            CreatedBy = doc.GetValue("createdBy", "").AsString,
            CreatedByName = doc.GetValue("createdByName", "").AsString,
            OrganizationId = doc.GetValue("organizationId", "").AsString,
            IsActive = doc.GetValue("isActive", true).AsBoolean,
            Version = doc.GetValue("version", 1).AsInt32,
            CreatedAt = doc.GetValue("createdAt", DateTime.UtcNow).ToUniversalTime(),
            UpdatedAt = doc.GetValue("updatedAt", DateTime.UtcNow).ToUniversalTime()
        };
    }
}
