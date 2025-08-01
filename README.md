<div align="center">

<img src="assets/logo.png" alt="Project Logo" width="200"/>


![Telegram Media Downloader](https://img.shields.io/badge/Telegram-Media%20Downloader-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-orange?style=for-the-badge)

[![Get Started](https://img.shields.io/badge/Get%20Started-Quick%20Start-blue?style=for-the-badge&logo=github)](QUICK_START.md)
[![Documentation](https://img.shields.io/badge/Documentation-README-blue?style=for-the-badge&logo=markdown)](README.md)
[![Issues](https://img.shields.io/badge/Issues-Report%20Bug-red?style=for-the-badge&logo=github)](https://github.com/1BitCode-Com/telegram-media-downloader/issues)

</div>

---

# Telegram Media Downloader

A powerful and efficient Python script for downloading media files from Telegram groups and channels with advanced features and human-like behavior.

## Features

### Core Features
- **Media Download**: Download photos, videos, documents, and audio files
- **Resume Support**: Automatically resume downloads from where you left off
- **Date Organization**: Files are organized by date (YYYY-MM format)
- **Human-like Behavior**: Random delays and natural download patterns
- **Account Type Support**: Optimized settings for both free and premium accounts
- **Target Configuration**: Set default group/channel in config file

### Advanced Features
- **Concurrent Downloads**: Download multiple files simultaneously
- **Date Filtering**: Filter downloads by specific date ranges
- **Password Protection**: Support for password-protected channels
- **CSV Export**: Export download reports to CSV format
- **State Encryption**: Secure state file encryption
- **Memory Monitoring**: Real-time memory usage tracking
- **Automatic Cleanup**: Remove temporary and old files
- **File Size Limits**: Configurable file size restrictions
- **Extension Filtering**: Download only specific file types
- **Duplicate File Handling**: Overwrite or create unique names for existing files

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram account (free or premium)
- API credentials from [my.telegram.org](https://my.telegram.org)

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

3. **Run the interactive setup:**
```bash
python3 run.py
```

### Interactive Setup

The script provides an interactive setup that guides you through:

1. **API Credentials**: Enter your `api_id` and `api_hash`
2. **Download Directory**: Choose where to save files
3. **Target Group/Channel**: Set the default group to download from
4. **Account Type**: Select free or premium account
5. **File Size Limits**: Set maximum file size or ignore limits
6. **Media Types**: Choose which types to download

## Configuration

### Basic Configuration

Edit `config.json` to customize settings:

```json
{
  "api_id": "YOUR_API_ID",
  "api_hash": "YOUR_API_HASH",
  "session_name": "telegram_downloader",
  "target_group": "https://t.me/example_channel",
  "download_dir": "/path/to/downloads",
  "account_type": "premium",
  "max_concurrent": 3,
  "batch_size": 8,
  "delay_between_batches": 8,
  "overwrite_existing_files": true
}
```

### Target Group Configuration

You can set a default group/channel in the config file:

```json
{
  "target_group": "https://t.me/example_channel"
}
```

**Supported formats:**
- `https://t.me/channel_name`
- `@channel_name`
- `channel_name`
- `https://t.me/joinchat/abcdef123456` (private channels)

### Account Type Settings

#### Premium Account (Recommended)
```json
{
  "account_type": "premium",
  "premium_settings": {
    "max_concurrent": 3,
    "delay_between_batches": 8,
    "batch_size": 8
  }
}
```

#### Free Account (Conservative)
```json
{
  "account_type": "free",
  "free_settings": {
    "max_concurrent": 1,
    "delay_between_batches": 15,
    "batch_size": 5
  }
}
```

## Usage

### Command Line Usage

```bash
# Use target from config.json
python3 telegram_media_downloader.py

# Override target from command line
python3 telegram_media_downloader.py --target "https://t.me/channel_name"

# With custom config
python3 telegram_media_downloader.py --config custom_config.json

# Ignore file size limits
python3 telegram_media_downloader.py --ignore-size-limit

# Overwrite existing files
python3 telegram_media_downloader.py --overwrite

# Date filtering
python3 telegram_media_downloader.py --start-date 2024-01-01 --end-date 2024-12-31

# Password protected channel
python3 telegram_media_downloader.py --password "channel_password" --target "https://t.me/private_channel"
```

### Interactive Mode

```bash
# Start interactive setup
python3 run.py

# Quick start guide
python3 quick_start.py
```

### Target Group Priority

The script uses target groups in this order:

1. **Command line argument** (`--target`) - Highest priority
2. **Config file** (`target_group`) - If no command line argument
3. **Interactive input** - If neither is provided

## File Organization

### Automatic Date-Based Organization
Files are automatically organized by date:

```
downloads/
├── 2024-01/
│   ├── photo_123.jpg
│   ├── document_456.pdf
│   └── video_789.mp4
├── 2024-02/
│   ├── photo_101.jpg
│   └── audio_202.mp3
└── 2024-03/
    └── photo_303.jpg
```

### File Naming Convention
- **Photos**: `photo_[message_id].jpg`
- **Documents**: Original filename preserved
- **Videos**: Original filename preserved
- **Duplicates**: `filename_1.ext`, `filename_2.ext`

### Supported File Types
- **Images**: jpg, jpeg, png, gif
- **Videos**: mp4, avi, mov
- **Documents**: pdf, doc, docx, txt, sql, csv, json, xml
- **Archives**: zip, rar
- **Audio**: mp3, wav

## Performance Tips

### For Premium Accounts
- Use 3-5 concurrent downloads
- 8-10 second delays between batches
- 8-10 files per batch

### For Free Accounts
- Use 1 concurrent download
- 15-20 second delays between batches
- 5 files per batch

### Rate Limiting Guidelines

| Account Type | Max Concurrent | Delay (seconds) | Batch Size |
|--------------|----------------|-----------------|------------|
| Free         | 1              | 15-20           | 5          |
| Premium      | 3-5            | 8-10            | 8-10       |

## Troubleshooting

### Common Issues

#### FloodWaitError
**Problem**: Telegram rate limiting
**Solution**: 
- Increase delays between batches
- Reduce concurrent downloads
- Switch to free account settings

#### Connection Issues
**Problem**: Network connectivity problems
**Solution**:
- Check internet connection
- Verify API credentials
- Try different session name

#### Large Files
**Problem**: Files too large to download
**Solution**:
- Set `ignore_file_size_limit: true`
- Increase `max_file_size_mb`
- Use premium account

#### Memory Issues
**Problem**: High memory usage
**Solution**:
- Reduce batch size
- Enable automatic cleanup
- Monitor memory usage

#### Target Group Issues
**Problem**: Cannot access target group/channel
**Solution**:
- Verify group link is correct
- Check if group is public or you have access
- Use password for private channels
- Try different link format

### Error Messages

```
ERROR: FloodWaitError - Too many requests
```
→ Increase delays, reduce concurrent downloads

```
ERROR: Session password required
```
→ Add `--password` parameter

```
ERROR: File too large
```
→ Set `ignore_file_size_limit: true`

```
ERROR: Target is required!
```
→ Set `target_group` in config.json or use `--target` argument

## Advanced Features

### Resume Downloads
The script automatically saves progress and can resume from where it stopped:

```bash
# Stop the script (Ctrl+C)
# Restart later - it will resume automatically
python3 telegram_media_downloader.py
```

### CSV Export
Export download statistics to CSV:

```json
{
  "csv_export": true
}
```

### State Encryption
Encrypt state files for security:

```json
{
  "encryption_key": "your-secret-key-here"
}
```

### Memory Monitoring
Track memory usage in real-time:

```json
{
  "memory_limit_mb": 1000
}
```

### Target Group Management
Set and manage target groups:

```json
{
  "target_group": "https://t.me/example_channel"
}
```

### Duplicate File Handling
Control how the script handles existing files:

```json
{
  "overwrite_existing_files": true
}
```

**Options:**
- `true`: Overwrite existing files (saves space)
- `false`: Create unique names (preserves old files)

**Command line:**
```bash
# Overwrite existing files
python3 telegram_media_downloader.py --overwrite

# Create unique names (default)
python3 telegram_media_downloader.py
```

## Development

### Project Structure
```
telegram-media-downloader/
├── telegram_media_downloader.py  # Main script
├── run.py                        # Interactive runner
├── quick_start.py                # Quick start guide
├── config.json                   # Configuration
├── requirements.txt              # Dependencies
├── utils/                        # Utility modules
├── logs/                         # Log files
└── downloads/                    # Downloaded files
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Testing
```bash
# Run tests
python3 test_downloader.py

# Test configuration
python3 -c "import telegram_media_downloader"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check [QUICK_START.md](QUICK_START.md) for detailed guide
- **Security**: Report security issues privately

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes and updates.

---

<div align="center">

**Made with ❤️ by [1BitCode-Com](https://github.com/1BitCode-Com)**

<img src="assets/banner.png" alt="Project Banner" width="800"/>

</div> 
