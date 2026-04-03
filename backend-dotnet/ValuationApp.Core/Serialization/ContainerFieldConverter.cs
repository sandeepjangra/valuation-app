using System.Text.Json;
using System.Text.Json.Serialization;
using ValuationApp.Core.DTOs;

namespace ValuationApp.Core.Serialization;

/// <summary>
/// Custom JSON converter to serialize all container types with $type: "container"
/// and include the container property to distinguish between TabGroup, Tab, Section, Group
/// </summary>
public class ContainerFieldConverter : JsonConverter<ContainerField>
{
    public override ContainerField Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        using var doc = JsonDocument.ParseValue(ref reader);
        var root = doc.RootElement;

        // Read the container type
        if (!root.TryGetProperty("container", out var containerElement))
        {
            throw new JsonException("Missing 'container' property in ContainerField");
        }

        var containerType = containerElement.GetString();
        
        // Deserialize to the appropriate type based on container value
        ContainerField field = containerType switch
        {
            "TabGroup" => JsonSerializer.Deserialize<TabGroupField>(root.GetRawText(), options)!,
            "Tab" => JsonSerializer.Deserialize<TabField>(root.GetRawText(), options)!,
            "Section" => JsonSerializer.Deserialize<SectionField>(root.GetRawText(), options)!,
            "Group" => JsonSerializer.Deserialize<GroupField>(root.GetRawText(), options)!,
            _ => throw new JsonException($"Unknown container type: {containerType}")
        };

        return field;
    }

    public override void Write(Utf8JsonWriter writer, ContainerField value, JsonSerializerOptions options)
    {
        writer.WriteStartObject();
        
        // Write $type as "container" for all container types
        writer.WriteString("$type", "container");
        
        // Write the container enum value as string
        writer.WriteString("container", value.Container.ToString());
        
        // Write fieldId, label, displayOrder
        writer.WriteString("fieldId", value.FieldId);
        writer.WriteString("label", value.Label);
        writer.WriteNumber("displayOrder", value.DisplayOrder);
        writer.WriteNumber("fieldType", (int)value.FieldType);
        writer.WriteBoolean("isVisible", value.IsVisible);
        
        // Write visibility if present
        if (value.Visibility != null)
        {
            writer.WritePropertyName("visibility");
            JsonSerializer.Serialize(writer, value.Visibility, options);
        }
        
        // Write type-specific properties
        switch (value)
        {
            case TabGroupField tabGroup:
                writer.WritePropertyName("children");
                JsonSerializer.Serialize(writer, tabGroup.Children, options);
                break;
                
            case TabField tab:
                writer.WritePropertyName("children");
                JsonSerializer.Serialize(writer, tab.Children, options);
                break;
                
            case SectionField section:
                writer.WritePropertyName("children");
                JsonSerializer.Serialize(writer, section.Children, options);
                writer.WriteBoolean("isCollapsible", section.IsCollapsible);
                writer.WriteBoolean("isCollapsed", section.IsCollapsed);
                break;
                
            case GroupField group:
                writer.WritePropertyName("children");
                JsonSerializer.Serialize(writer, group.Children, options);
                writer.WriteBoolean("isCollapsible", group.IsCollapsible);
                writer.WriteBoolean("isCollapsed", group.IsCollapsed);
                break;
        }
        
        writer.WriteEndObject();
    }
}
