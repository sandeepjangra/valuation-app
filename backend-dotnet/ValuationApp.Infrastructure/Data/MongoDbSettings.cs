namespace ValuationApp.Infrastructure.Data;

/// <summary>
/// MongoDB database settings
/// </summary>
public class MongoDbSettings
{
    public string ConnectionString { get; set; } = string.Empty;
    public string AdminDatabaseName { get; set; } = "valuation_admin";
    public string ReportsDatabaseName { get; set; } = "valuation_reports";
}
