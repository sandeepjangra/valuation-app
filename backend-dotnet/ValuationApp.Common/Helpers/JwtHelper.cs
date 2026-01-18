using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace ValuationApp.Common.Helpers;

/// <summary>
/// JWT Token Helper for generating and validating JWT tokens
/// </summary>
public class JwtHelper
{
    private readonly string _secret;
    private readonly string _issuer;
    private readonly string _audience;
    private readonly int _expiryHours;

    public JwtHelper(string secret, string issuer, string audience, int expiryHours = 24)
    {
        _secret = secret;
        _issuer = issuer;
        _audience = audience;
        _expiryHours = expiryHours;
    }

    /// <summary>
    /// Generate JWT access token
    /// </summary>
    public string GenerateAccessToken(Dictionary<string, object> claims, int? customExpiryHours = null)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.UTF8.GetBytes(_secret);
        
        var claimsList = new List<Claim>
        {
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(JwtRegisteredClaimNames.Iat, DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
        };

        foreach (var claim in claims)
        {
            if (claim.Value != null)
            {
                claimsList.Add(new Claim(claim.Key, claim.Value.ToString()!));
            }
        }

        var expiryTime = customExpiryHours ?? _expiryHours;
        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claimsList),
            Expires = DateTime.UtcNow.AddHours(expiryTime),
            Issuer = _issuer,
            Audience = _audience,
            SigningCredentials = new SigningCredentials(
                new SymmetricSecurityKey(key),
                SecurityAlgorithms.HmacSha256Signature)
        };

        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }

    /// <summary>
    /// Generate JWT ID token (similar to access token but for identity)
    /// </summary>
    public string GenerateIdToken(Dictionary<string, object> claims, int? customExpiryHours = null)
    {
        // For simplicity, ID token is the same as access token
        // In production, you might want different claims or expiry
        return GenerateAccessToken(claims, customExpiryHours);
    }

    /// <summary>
    /// Generate refresh token (longer expiry)
    /// </summary>
    public string GenerateRefreshToken(Dictionary<string, object> claims)
    {
        // Refresh token has 7 days expiry
        return GenerateAccessToken(claims, 24 * 7);
    }

    /// <summary>
    /// Validate JWT token
    /// </summary>
    public ClaimsPrincipal? ValidateToken(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_secret);

            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = true,
                ValidIssuer = _issuer,
                ValidateAudience = true,
                ValidAudience = _audience,
                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero
            };

            var principal = tokenHandler.ValidateToken(token, validationParameters, out _);
            return principal;
        }
        catch
        {
            return null;
        }
    }
}
