# MongoDB Backup System

Comprehensive backup and restore system for MongoDB Atlas databases.

## 🎯 Features

- ✅ Full database backup to local JSON files
- ✅ Restore from previous backups
- ✅ Backup metadata and statistics
- ✅ Index preservation
- ✅ Multiple database support
- ✅ Timestamp-based backup organization
- ✅ Easy-to-use command-line interface

## 📋 Prerequisites

1. Python 3.7 or higher
2. Required Python packages (install with pip):
   ```bash
   pip install pymongo python-dotenv
   ```
3. `.env` file with `MONGODB_URI` configured

## 🚀 Quick Start

### Create a Backup

```bash
# Using the convenience script (recommended)
./scripts/run_backup.sh backup

# Or directly with Python
python3 scripts/backup_mongodb.py --action backup
```

### List Available Backups

```bash
# Using the convenience script
./scripts/run_backup.sh list

# Or directly with Python
python3 scripts/backup_mongodb.py --action list
```

### Restore from Backup

```bash
# Using the convenience script
./scripts/run_backup.sh restore 20231123_145030

# Or directly with Python
python3 scripts/backup_mongodb.py --action restore --timestamp 20231123_145030
```

## 📁 Backup Structure

Backups are stored in the `backups/` directory with the following structure:

```
backups/
└── backup_20231123_145030/
    ├── backup_metadata.json          # Backup statistics
    ├── valuation_app_prod/           # Main database
    │   ├── banks.json
    │   ├── banks_indexes.json
    │   ├── common_form_fields.json
    │   └── ...
    ├── valuation_admin/              # Admin database
    │   └── ...
    └── valuation_reports/            # Reports database
        └── ...
```

## 🔧 Advanced Usage

### Backup Specific Databases

```bash
# Backup only specific databases
python3 scripts/backup_mongodb.py --action backup --databases valuation_app_prod valuation_admin

# Restore only specific databases
python3 scripts/backup_mongodb.py --action restore --timestamp 20231123_145030 --databases valuation_app_prod
```

### Custom Backup Directory

```bash
# Specify custom backup location
python3 scripts/backup_mongodb.py --action backup --backup-dir /path/to/backups
```

### Full Command-Line Options

```bash
python3 scripts/backup_mongodb.py --help

Options:
  --action {backup,restore,list}  Action to perform (default: backup)
  --databases [DB1 DB2 ...]       Specific databases to backup/restore
  --timestamp TIMESTAMP           Timestamp of backup to restore
  --backup-dir DIRECTORY          Custom backup directory
```

## 📊 Backup Metadata

Each backup includes a `backup_metadata.json` file with:

- Backup timestamp
- List of databases backed up
- Number of collections per database
- Number of documents per collection
- Total document count
- File paths and sizes

Example:
```json
{
  "timestamp": "20231123_145030",
  "backup_path": "/path/to/backups/backup_20231123_145030",
  "databases": {
    "valuation_app_prod": {
      "collections_count": 5,
      "total_documents": 1247,
      "collections": {
        "banks": {
          "document_count": 15,
          "file_size_bytes": 45678
        }
      }
    }
  },
  "total_documents": 1247,
  "total_collections": 5
}
```

## 🔄 Restore Process

⚠️ **WARNING**: Restoring a backup will **overwrite** existing data!

The restore process:
1. Prompts for confirmation
2. Drops existing collections
3. Restores documents from backup
4. Recreates indexes

## ⏰ Scheduled Backups

### Option 1: Cron (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/ValuationAppV1 && ./scripts/run_backup.sh backup >> logs/backup.log 2>&1

# Weekly backup every Sunday at 3 AM
0 3 * * 0 cd /path/to/ValuationAppV1 && ./scripts/run_backup.sh backup >> logs/backup_weekly.log 2>&1
```

### Option 2: macOS LaunchAgent

Create `~/Library/LaunchAgents/com.valuationapp.backup.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.valuationapp.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/ValuationAppV1/scripts/run_backup.sh</string>
        <string>backup</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.valuationapp.backup.plist
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `python3`
6. Arguments: `scripts/backup_mongodb.py --action backup`
7. Start in: `/path/to/ValuationAppV1`

## 💡 Best Practices

1. **Regular Backups**: Schedule daily backups at off-peak hours
2. **Retention Policy**: Keep last 7 daily backups, 4 weekly backups
3. **Test Restores**: Periodically test restore process
4. **Off-site Storage**: Copy backups to cloud storage or external drive
5. **Monitoring**: Check backup logs regularly
6. **Documentation**: Document backup/restore procedures

## 🗑️ Backup Cleanup

To manage disk space, regularly clean old backups:

```bash
# Keep only last 7 backups (manual cleanup)
cd backups/
ls -t | tail -n +8 | xargs rm -rf

# Or create a cleanup script
#!/bin/bash
BACKUP_DIR="backups"
KEEP_DAYS=7
find "$BACKUP_DIR" -type d -name "backup_*" -mtime +$KEEP_DAYS -exec rm -rf {} \;
```

## 🔐 Security Notes

1. Backup files contain sensitive data - restrict access
2. Use appropriate file permissions (700 for backup directory)
3. Encrypt backups if storing off-site
4. Never commit backups to version control
5. Add `backups/` to `.gitignore`

## 🐛 Troubleshooting

### Connection Errors

```
❌ Failed to connect to MongoDB
```
**Solution**: Check `.env` file has correct `MONGODB_URI`

### Permission Errors

```
❌ Permission denied: backups/
```
**Solution**: Create backup directory and set permissions
```bash
mkdir -p backups
chmod 700 backups
```

### Missing Dependencies

```
❌ ModuleNotFoundError: No module named 'pymongo'
```
**Solution**: Install required packages
```bash
pip install pymongo python-dotenv
```

### Large Backups

For very large databases:
- Consider database-specific backups
- Use MongoDB's native mongodump for better performance
- Implement incremental backups

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backup logs in `logs/backup.log`
3. Contact the development team

## 📝 Changelog

### Version 1.0.0 (2023-11-23)
- Initial release
- Full backup and restore functionality
- Metadata tracking
- Index preservation
- Multi-database support
