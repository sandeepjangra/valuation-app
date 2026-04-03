using System.Text.Json;
using System.Text.Json.Serialization;
using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Serialization;

/// <summary>
/// Custom JSON converter for BaseField that handles polymorphic serialization
/// including special handling for ContainerField types
/// </summary>
public class BaseFieldConverter : JsonConverter<BaseField>
{
    private readonly ContainerFieldConverter _containerConverter = new();

    public override BaseField Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        using var doc = JsonDocument.ParseValue(ref reader);
        var root = doc.RootElement;

        // Read the $type discriminator
        if (!root.TryGetProperty("$type", out var typeElement))
        {
            throw new JsonException("Missing '$type' property in BaseField");
        }

        var type = typeElement.GetString();
        
        // Handle different types
        return type switch
        {
            "input" => JsonSerializer.Deserialize<InputField>(root.GetRawText(), options)!,
            "table" => JsonSerializer.Deserialize<TableField>(root.GetRawText(), options)!,
            "attachment" => JsonSerializer.Deserialize<AttachmentField>(root.GetRawText(), options)!,
            "container" => DeserializeContainer(root, options),
            _ => throw new JsonException($"Unknown $type: {type}")
        };
    }

    private BaseField DeserializeContainer(JsonElement root, JsonSerializerOptions options)
    {
        // Read the container type to determine which concrete type to create
        if (!root.TryGetProperty("container", out var containerElement))
        {
            throw new JsonException("Missing 'container' property in container field");
        }

        var containerType = containerElement.GetString();
        
        return containerType switch
        {
            "TabGroup" => JsonSerializer.Deserialize<TabGroupField>(root.GetRawText(), options)!,
            "Tab" => JsonSerializer.Deserialize<TabField>(root.GetRawText(), options)!,
            "Section" => JsonSerializer.Deserialize<SectionField>(root.GetRawText(), options)!,
            "Group" => JsonSerializer.Deserialize<GroupField>(root.GetRawText(), options)!,
            _ => throw new JsonException($"Unknown container type: {containerType}")
        };
    }

    public override void Write(Utf8JsonWriter writer, BaseField value, JsonSerializerOptions options)
    {
        // For container types, use the ContainerFieldConverter
        if (value is ContainerField containerField)
        {
            _containerConverter.Write(writer, containerField, options);
            return;
        }

        // For other types, use default serialization with $type discriminator
        writer.WriteStartObject();
        
        switch (value)
        {
            case InputField input:
                writer.WriteString("$type", "input");
                WriteInputField(writer, input, options);
                break;
                
            case TableField table:
                writer.WriteString("$type", "table");
                WriteTableField(writer, table, options);
                break;
                
            case AttachmentField attachment:
                writer.WriteString("$type", "attachment");
                WriteAttachmentField(writer, attachment, options);
                break;
        }
        
        writer.WriteEndObject();
    }

    private void WriteInputField(Utf8JsonWriter writer, InputField field, JsonSerializerOptions options)
    {
        WriteBaseProperties(writer, field);
        writer.WriteNumber("specificType", (int)field.SpecificType);
        
        if (field.DefaultValue != null)
            writer.WriteString("defaultValue", field.DefaultValue);
            
        writer.WriteBoolean("isRequired", field.IsRequired);
        writer.WriteBoolean("isReadonly", field.IsReadonly);
        
        if (field.HelpText != null)
            writer.WriteString("helpText", field.HelpText);
            
        if (field.PlaceholderText != null)
            writer.WriteString("placeholderText", field.PlaceholderText);
            
        if (field.Options != null)
        {
            writer.WritePropertyName("options");
            JsonSerializer.Serialize(writer, field.Options, options);
        }
        
        if (field.ValidationRules != null)
        {
            writer.WritePropertyName("validationRules");
            JsonSerializer.Serialize(writer, field.ValidationRules, options);
        }
    }

    private void WriteTableField(Utf8JsonWriter writer, TableField field, JsonSerializerOptions options)
    {
        WriteBaseProperties(writer, field);
        
        writer.WritePropertyName("columns");
        JsonSerializer.Serialize(writer, field.Columns, options);
        
        if (field.Rows != null)
        {
            writer.WritePropertyName("rows");
            JsonSerializer.Serialize(writer, field.Rows, options);
        }
        
        writer.WritePropertyName("summaries");
        JsonSerializer.Serialize(writer, field.Summaries, options);
        
        writer.WriteNumber("minRows", field.MinRows);
        
        if (field.MaxRows.HasValue)
            writer.WriteNumber("maxRows", field.MaxRows.Value);
            
        writer.WriteBoolean("allowAddRows", field.AllowAddRows);
        writer.WriteBoolean("allowDeleteRows", field.AllowDeleteRows);
        writer.WriteBoolean("showFooter", field.ShowFooter);
    }

    private void WriteAttachmentField(Utf8JsonWriter writer, AttachmentField field, JsonSerializerOptions options)
    {
        WriteBaseProperties(writer, field);
        
        if (field.AllowedExtensions != null)
        {
            writer.WritePropertyName("allowedExtensions");
            JsonSerializer.Serialize(writer, field.AllowedExtensions, options);
        }
        
        writer.WriteNumber("maxFileSize", field.MaxFileSize);
        writer.WriteBoolean("allowMultiple", field.AllowMultiple);
        writer.WriteNumber("category", (int)field.Category);
    }

    private void WriteBaseProperties(Utf8JsonWriter writer, BaseField field)
    {
        writer.WriteString("fieldId", field.FieldId);
        writer.WriteString("label", field.Label);
        writer.WriteNumber("displayOrder", field.DisplayOrder);
        writer.WriteNumber("fieldType", (int)field.FieldType);
        writer.WriteBoolean("isVisible", field.IsVisible);
        
        if (field.Visibility != null)
        {
            writer.WritePropertyName("visibility");
            JsonSerializer.Serialize(writer, field.Visibility, new JsonSerializerOptions());
        }
    }
}
