# Telegram Media Downloader

<div align="center">

![Telegram Media Downloader](https://img.shields.io/badge/Telegram-Media%20Downloader-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-orange?style=for-the-badge)
![Downloads](https://img.shields.io/badge/Downloads-1000+-brightgreen?style=for-the-badge)

*A powerful Python script for downloading media files from Telegram groups and channels with advanced features like resume capability, concurrent downloads, and intelligent rate limiting.*

![Logo](assets/logo.svg)

[![Get Started](https://img.shields.io/badge/Get%20Started-Quick%20Start-blue?style=for-the-badge&logo=github)](QUICK_START.md)
[![Documentation](https://img.shields.io/badge/Documentation-README-blue?style=for-the-badge&logo=markdown)](README.md)
[![Issues](https://img.shields.io/badge/Issues-Report%20Bug-red?style=for-the-badge&logo=github)](https://github.com/1BitCode-Com/telegram-media-downloader/issues)

</div>

---

## Features

- Download media from public and private Telegram groups/channels
- Resume downloads from where you left off
- Support for 25,000+ files with intelligent batching
- Concurrent downloads with configurable limits
- Date-based file organization
- Progress tracking and detailed logging
- Rate limiting protection to avoid Telegram bans
- File type and size filtering
- Memory usage monitoring
- Automatic cleanup and state management

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Telegram API credentials (api_id and api_hash)

### Installation

1. **Clone or download the project:**
```bash
git clone https://github.com/1BitCode-Com/telegram-media-downloader.git
cd telegram-media-downloader
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Get your Telegram API credentials:**
   - Visit https://my.telegram.org/
   - Log in with your phone number
   - Create a new application
   - Copy the API ID and API Hash

### Usage

#### Method 1: Interactive Setup (Recommended)
```bash
python3 run.py
```

#### Method 2: Command Line
```bash
python3 telegram_media_downloader.py --target "https://t.me/groupname"
```

#### Method 3: Custom Directory
```bash
python3 telegram_media_downloader.py --target "group" --download-dir "/path/to/downloads"
```

#### Method 4: Save API Credentials
```bash
python3 telegram_media_downloader.py --api-id "YOUR_ID" --api-hash "YOUR_HASH" --save-credentials
```

## Configuration

### Default Settings (Safe for Free Accounts)

```json
{
  "max_concurrent": 3,
  "delay_between_batches": 5,
  "batch_size": 20,
  "account_type": "free"
}
```

### Premium Account Settings

```json
{
  "account_type": "premium",
  "max_concurrent": 10,
  "delay_between_batches": 3,
  "batch_size": 50
}
```

## Advanced Features

### Concurrent Downloads
Enable multiple simultaneous downloads:
```bash
python3 telegram_media_downloader.py --target "group" --max-concurrent 5
```

### Date Filtering
Download files from specific date range:
```bash
python3 telegram_media_downloader.py --target "group" --start-date "2025-01-01" --end-date "2025-12-31"
```

### Password-Protected Channels
Access private channels with password:
```bash
python3 telegram_media_downloader.py --target "private_channel" --password "channel_password"
```

### CSV Export
Export download statistics to CSV:
```bash
python3 telegram_media_downloader.py --target "group" --csv-export
```

### Ignore File Size Limits
Download all files regardless of size:
```bash
python3 telegram_media_downloader.py --target "group" --ignore-size-limit
```

## Troubleshooting

### Common Issues

#### 1. FloodWaitError - Rate Limiting
**Problem:** Telegram is blocking requests due to high speed
```
Sleeping for 1s (0:00:01) on GetFileRequest flood wait
```

**Solutions:**
- Reduce `max_concurrent` to 3-5
- Increase `delay_between_batches` to 5-10 seconds
- Use `account_type: "free"` settings
- Wait 1-2 hours before retrying

#### 2. Connection Issues
**Problem:** Cannot connect to Telegram servers

**Solutions:**
- Check internet connection
- Verify API credentials
- Try using VPN if blocked
- Check if Telegram is accessible in your region

#### 3. Large File Downloads
**Problem:** Files are being skipped due to size limits

**Solutions:**
- Use `--ignore-size-limit` flag
- Increase `max_file_size_mb` in config.json
- Ensure sufficient disk space

#### 4. Memory Issues
**Problem:** High memory usage during downloads

**Solutions:**
- Reduce `max_concurrent` to 2-3
- Decrease `batch_size` to 10-20
- Enable automatic cleanup in config

### Performance Tips

#### For Free Accounts:
- Use `max_concurrent: 3`
- Set `delay_between_batches: 5`
- Keep `batch_size: 20`
- Avoid downloading during peak hours

#### For Premium Accounts:
- Use `max_concurrent: 10`
- Set `delay_between_batches: 3`
- Increase `batch_size: 50`
- Monitor memory usage

### Rate Limiting Guidelines

| Account Type | Max Concurrent | Delay (seconds) | Batch Size |
|-------------|----------------|-----------------|------------|
| Free        | 3              | 5               | 20         |
| Premium     | 10             | 3               | 50         |

## File Organization

Files are organized by date in the download directory:
```
downloads/
├── 2025-07-31/
│   ├── photo_001.jpg
│   ├── video_002.mp4
│   └── document_003.pdf
└── 2025-08-01/
    └── ...
```

## Supported File Types

### Images
- JPG, JPEG, PNG, GIF

### Videos
- MP4, AVI, MOV

### Documents
- PDF, DOC, DOCX, ZIP, RAR

### Text Files
- TXT, SQL, CSV, JSON, XML

### Audio
- MP3, WAV

## Telegram Account Types and Limits

### Free Account Limits
- **Concurrent Downloads:** 3-5
- **Batch Size:** 20-50 files
- **Delay Between Requests:** 5-10 seconds
- **Daily Download Limit:** ~2GB

### Premium Account Benefits
- **Concurrent Downloads:** 10-20
- **Batch Size:** 50-200 files
- **Delay Between Requests:** 1-3 seconds
- **Daily Download Limit:** ~4GB
- **Faster Download Speeds**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/1BitCode-Com/telegram-media-downloader/issues)
- **Discussions:** [GitHub Discussions](https://github.com/1BitCode-Com/telegram-media-downloader/discussions)
- **Security:** [Security Policy](SECURITY.md)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes.

---

<div align="center">

**Made with ❤️ by [1BitCode-Com](https://github.com/1BitCode-Com)**

[![GitHub](https://img.shields.io/badge/GitHub-1BitCode--Com-black?style=for-the-badge&logo=github)](https://github.com/1BitCode-Com)
[![Telegram](https://img.shields.io/badge/Telegram-Contact-blue?style=for-the-badge&logo=telegram)](https://t.me/1BitCode)

</div> 