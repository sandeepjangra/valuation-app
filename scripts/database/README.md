# Database Scripts

Scripts for MongoDB Atlas setup, migrations, and maintenance.

## Initial Setup Scripts

### `setup_mongodb_atlas.py`
Initial MongoDB Atlas configuration.

**What it does:**
- Creates database connections
- Sets up authentication
- Configures initial settings

**Usage:**
```bash
python scripts/database/setup_mongodb_atlas.py
```

### `create_mongodb_collections.py`
Creates all required collections in the database.

**Collections created:**
- `organizations`
- `users`
- `banks`
- `common_fields`
- Bank-specific collections (SBI, PNB, UBI, etc.)

**Usage:**
```bash
python scripts/database/create_mongodb_collections.py
```

### `setup_banks_collection.py`
Sets up the banks master collection with all supported banks.

**Usage:**
```bash
python scripts/database/setup_banks_collection.py
```

### `setup_common_fields_collection.py`
Creates common fields used across all bank templates.

**Usage:**
```bash
python scripts/database/setup_common_fields_collection.py
```

## Maintenance Scripts

### `refresh_collections.py`
Refreshes collection data from templates.

**Use cases:**
- After template updates
- When data gets corrupted
- To reset to default state

**Usage:**
```bash
python scripts/database/refresh_collections.py
```

### `cleanup_collections.py`
Cleans up unused or test collections.

**Warning:** This deletes data. Use with caution!

**Usage:**
```bash
python scripts/database/cleanup_collections.py
```

### `migrate_databases.py`
Runs database migrations for schema changes.

**Usage:**
```bash
python scripts/database/migrate_databases.py
```

## Bank-Specific Scripts

Located in main `scripts/` directory (to be moved here):
- `create_sbi_apartment_collection.py`
- `create_ubi_land_collection.py`
- `recreate_sbi_land_collection.py`
- `recreate_ubi_land_collection.py`

## Best Practices

1. **Always backup** before running any database script
2. **Test in development** first
3. **Check MongoDB Atlas connection** before running
4. **Review script output** for errors
5. **Use transactions** where possible for data integrity

## Common Workflows

### Fresh Database Setup
```bash
# 1. Setup MongoDB Atlas connection
python scripts/database/setup_mongodb_atlas.py

# 2. Create all collections
python scripts/database/create_mongodb_collections.py

# 3. Setup banks
python scripts/database/setup_banks_collection.py

# 4. Setup common fields
python scripts/database/setup_common_fields_collection.py
```

### Refresh All Data
```bash
python scripts/database/refresh_collections.py
```

### Clean Up Test Data
```bash
python scripts/database/cleanup_collections.py
```

## Environment Variables Required

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=valuationapp
```

## Troubleshooting

**Connection Error:** Verify MongoDB Atlas URI and network access settings
**Collection Already Exists:** Use refresh or cleanup scripts
**Permission Denied:** Check database user permissions in Atlas
**Timeout:** Check network connectivity and Atlas cluster status
