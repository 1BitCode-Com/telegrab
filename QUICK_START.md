# Quick Start Guide

## Prerequisites

- Python 3.7 or higher
- Telegram API credentials

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get API credentials:**
   - Visit https://my.telegram.org/
   - Create a new application
   - Copy API ID and API Hash

## Quick Setup

### Method 1: Interactive Setup
```bash
python3 run.py
```

### Method 2: Command Line
```bash
python3 telegram_media_downloader.py --target "https://t.me/groupname"
```

## Configuration

### Safe Settings (Recommended for Free Accounts)
```json
{
  "max_concurrent": 3,
  "delay_between_batches": 5,
  "batch_size": 20,
  "account_type": "free"
}
```

### Performance Settings (Premium Accounts)
```json
{
  "max_concurrent": 10,
  "delay_between_batches": 3,
  "batch_size": 50,
  "account_type": "premium"
}
```

## Common Issues & Solutions

### ⚠️ Rate Limiting (FloodWaitError)
**Problem:** `Sleeping for 1s on GetFileRequest flood wait`

**Quick Fix:**
```bash
# Reduce speed immediately
python3 telegram_media_downloader.py --target "group" --max-concurrent 2
```

**Prevention:**
- Use free account settings
- Avoid downloading during peak hours
- Wait 1-2 hours between large downloads

### 🔗 Connection Issues
**Problem:** Cannot connect to Telegram

**Solutions:**
- Check internet connection
- Verify API credentials
- Try using VPN
- Check if Telegram is accessible

### 💾 Large Files Skipped
**Problem:** Files not downloading due to size

**Solution:**
```bash
python3 telegram_media_downloader.py --target "group" --ignore-size-limit
```

### 🧠 Memory Issues
**Problem:** High memory usage

**Solution:**
```json
{
  "max_concurrent": 2,
  "batch_size": 10
}
```

## Performance Tips

### For Free Accounts:
- ✅ Use `max_concurrent: 3`
- ✅ Set `delay_between_batches: 5`
- ✅ Keep `batch_size: 20`
- ❌ Avoid downloading during peak hours

### For Premium Accounts:
- ✅ Use `max_concurrent: 10`
- ✅ Set `delay_between_batches: 3`
- ✅ Increase `batch_size: 50`
- ✅ Monitor memory usage

## Rate Limiting Guidelines

| Account Type | Max Concurrent | Delay (seconds) | Batch Size |
|-------------|----------------|-----------------|------------|
| Free        | 3              | 5               | 20         |
| Premium     | 10             | 3               | 50         |

## File Organization

Files are automatically organized by date:
```
downloads/
├── 2025-07-31/
│   ├── photo_001.jpg
│   └── video_002.mp4
└── 2025-08-01/
    └── document_003.pdf
```

## Supported File Types

### Images: JPG, JPEG, PNG, GIF
### Videos: MP4, AVI, MOV
### Documents: PDF, DOC, DOCX, ZIP, RAR
### Text: TXT, SQL, CSV, JSON, XML
### Audio: MP3, WAV

## Advanced Features

### Resume Downloads
```bash
# Automatically resumes from where it left off
python3 telegram_media_downloader.py --target "group"
```

### Date Filtering
```bash
# Download files from specific date range
python3 telegram_media_downloader.py --target "group" --start-date "2025-01-01" --end-date "2025-12-31"
```

### Custom Directory
```bash
# Download to custom location
python3 telegram_media_downloader.py --target "group" --download-dir "/path/to/downloads"
```

### Export Statistics
```bash
# Export download stats to CSV
python3 telegram_media_downloader.py --target "group" --csv-export
```

## Troubleshooting Checklist

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API credentials obtained from https://my.telegram.org/
- [ ] API credentials saved in config.json
- [ ] Target group/channel accessible
- [ ] Sufficient disk space
- [ ] Internet connection stable
- [ ] Using appropriate rate limiting settings

## Need Help?

- Check logs in `logs/downloader.log`
- Review [README.md](README.md) for detailed documentation
- Open an issue on GitHub for bugs
- Check troubleshooting section in README

---

**Remember:** Start with conservative settings and increase gradually to avoid rate limiting! 