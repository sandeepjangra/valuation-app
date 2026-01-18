using MongoDB.Driver;
using ValuationApp.Core.Entities;
using ValuationApp.Core.Interfaces;
using ValuationApp.Infrastructure.Data;

namespace ValuationApp.Infrastructure.Repositories;

/// <summary>
/// User repository implementation
/// </summary>
public class UserRepository : IUserRepository
{
    private readonly IMongoCollection<User> _users;

    public UserRepository(MongoDbContext context)
    {
        _users = context.GetAdminCollection<User>("users");
    }

    public async Task<User?> GetUserByEmailAsync(string email)
    {
        var filter = Builders<User>.Filter.Eq(u => u.Email, email.ToLower());
        return await _users.Find(filter).FirstOrDefaultAsync();
    }

    public async Task<User?> GetUserByUserIdAsync(string userId)
    {
        var filter = Builders<User>.Filter.Eq(u => u.UserId, userId);
        return await _users.Find(filter).FirstOrDefaultAsync();
    }

    public async Task UpdateLastLoginAsync(string userId)
    {
        var filter = Builders<User>.Filter.Eq(u => u.UserId, userId);
        var update = Builders<User>.Update
            .Set(u => u.LastLogin, DateTime.UtcNow)
            .Set(u => u.UpdatedAt, DateTime.UtcNow);
        
        await _users.UpdateOneAsync(filter, update);
    }

    public async Task<User> CreateUserAsync(User user)
    {
        await _users.InsertOneAsync(user);
        return user;
    }

    public async Task<bool> UpdateUserAsync(User user)
    {
        user.UpdatedAt = DateTime.UtcNow;
        var filter = Builders<User>.Filter.Eq(u => u.UserId, user.UserId);
        var result = await _users.ReplaceOneAsync(filter, user);
        return result.ModifiedCount > 0;
    }

    public async Task<List<User>> GetUsersByOrganizationAsync(string orgShortName, int skip = 0, int limit = 50)
    {
        var filter = Builders<User>.Filter.Eq(u => u.OrgShortName, orgShortName);
        return await _users.Find(filter)
            .Sort(Builders<User>.Sort.Descending(u => u.CreatedAt))
            .Skip(skip)
            .Limit(limit)
            .ToListAsync();
    }

    public async Task<long> GetUsersCountByOrganizationAsync(string orgShortName)
    {
        var filter = Builders<User>.Filter.Eq(u => u.OrgShortName, orgShortName);
        return await _users.CountDocumentsAsync(filter);
    }

    public async Task<bool> DeactivateUserAsync(string userId)
    {
        var filter = Builders<User>.Filter.Eq(u => u.UserId, userId);
        var update = Builders<User>.Update
            .Set(u => u.IsActive, false)
            .Set(u => u.Status, "inactive")
            .Set(u => u.UpdatedAt, DateTime.UtcNow);
        
        var result = await _users.UpdateOneAsync(filter, update);
        return result.ModifiedCount > 0;
    }

    public async Task<bool> UpdatePasswordAsync(string userId, string passwordHash)
    {
        var filter = Builders<User>.Filter.Eq(u => u.UserId, userId);
        var update = Builders<User>.Update
            .Set(u => u.PasswordHash, passwordHash)
            .Set(u => u.UpdatedAt, DateTime.UtcNow);
        
        var result = await _users.UpdateOneAsync(filter, update);
        return result.ModifiedCount > 0;
    }

    public async Task<bool> EmailExistsInOrganizationAsync(string email, string orgShortName)
    {
        var filter = Builders<User>.Filter.And(
            Builders<User>.Filter.Eq(u => u.Email, email.ToLower()),
            Builders<User>.Filter.Eq(u => u.OrgShortName, orgShortName)
        );
        var count = await _users.CountDocumentsAsync(filter);
        return count > 0;
    }
}
