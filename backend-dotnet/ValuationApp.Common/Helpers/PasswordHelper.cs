namespace ValuationApp.Common.Helpers;

/// <summary>
/// BCrypt password helper for password hashing and verification
/// </summary>
public static class PasswordHelper
{
    /// <summary>
    /// Verify a password against a bcrypt hash
    /// Compatible with Python's bcrypt $2b$ format
    /// </summary>
    public static bool VerifyPassword(string password, string passwordHash)
    {
        try
        {
            // BCrypt.Net-Next handles $2b$ prefix compatibility automatically
            return BCrypt.Net.BCrypt.Verify(password, passwordHash);
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>
    /// Hash a password using bcrypt
    /// </summary>
    public static string HashPassword(string password, int workFactor = 12)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, workFactor);
    }
}
