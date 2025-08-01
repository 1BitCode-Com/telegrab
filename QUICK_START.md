# Quick Start Guide

A comprehensive guide to get you started with Telegram Media Downloader quickly and efficiently.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet**: Stable connection required
- **Storage**: Sufficient space for downloads

### Telegram Requirements
- **Account**: Free or Premium Telegram account
- **API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
- **Access**: Join the target group/channel

## Installation

### Step 1: Download the Project
```bash
# Clone the repository
git clone https://github.com/1BitCode-Com/telegram-media-downloader.git

# Navigate to project directory
cd telegram-media-downloader
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or install manually
pip install telethon cryptg cryptography psutil
```

### Step 3: Get API Credentials
1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Create a new application
4. Copy the `api_id` and `api_hash`

## Quick Setup

### Method 1: Interactive Setup (Recommended)
```bash
# Run interactive setup
python3 run.py
```

The interactive setup will guide you through:
- API credentials entry
- Download directory selection
- Account type configuration
- File size limit settings

### Method 2: Manual Configuration
1. Edit `config.json`:
```json
{
  "api_id": "YOUR_API_ID",
  "api_hash": "YOUR_API_HASH",
  "download_dir": "/path/to/downloads",
  "account_type": "premium"
}
```

2. Run the script:
```bash
python3 telegram_media_downloader.py "https://t.me/channel_name"
```

## Configuration

### Safe Settings (Recommended for Beginners)

#### Free Account Settings
```json
{
  "account_type": "free",
  "max_concurrent": 1,
  "delay_between_batches": 15,
  "batch_size": 5,
  "max_file_size_mb": 10
}
```

#### Premium Account Settings
```json
{
  "account_type": "premium",
  "max_concurrent": 3,
  "delay_between_batches": 8,
  "batch_size": 8,
  "max_file_size_mb": 10
}
```

### Performance Settings (Advanced Users)

#### High Performance (Premium Only)
```json
{
  "account_type": "premium",
  "max_concurrent": 5,
  "delay_between_batches": 5,
  "batch_size": 10,
  "ignore_file_size_limit": true
}
```

#### Conservative Settings (Safe for All)
```json
{
  "account_type": "free",
  "max_concurrent": 1,
  "delay_between_batches": 20,
  "batch_size": 3,
  "max_file_size_mb": 5
}
```

## Usage Examples

### Basic Usage
```bash
# Download from public channel
python3 telegram_media_downloader.py "https://t.me/example_channel"

# Download from private group
python3 telegram_media_downloader.py "https://t.me/private_group"
```

### Advanced Usage
```bash
# Custom download directory
python3 telegram_media_downloader.py --download-dir "/media/pc/downloads" "https://t.me/channel"

# Ignore file size limits
python3 telegram_media_downloader.py --ignore-size-limit "https://t.me/channel"

# Date filtering
python3 telegram_media_downloader.py --start-date 2024-01-01 --end-date 2024-12-31 "https://t.me/channel"

# Password protected channel
python3 telegram_media_downloader.py --password "channel_password" "https://t.me/private_channel"
```

### Interactive Mode
```bash
# Start interactive setup
python3 run.py

# Quick start guide
python3 quick_start.py
```

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

## Supported File Types

### Images
- **JPG/JPEG**: Photos and images
- **PNG**: Transparent images
- **GIF**: Animated images

### Videos
- **MP4**: Most common video format
- **AVI**: Legacy video format
- **MOV**: Apple video format

### Documents
- **PDF**: Portable documents
- **DOC/DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **SQL**: Database files
- **CSV**: Spreadsheet data
- **JSON**: Data files
- **XML**: Markup files

### Archives
- **ZIP**: Compressed archives
- **RAR**: Compressed archives

### Audio
- **MP3**: Compressed audio
- **WAV**: Uncompressed audio

## Common Issues & Solutions

### Rate Limiting (FloodWaitError)
**Problem**: Telegram blocking requests due to high speed

**Solutions**:
1. **Increase delays**:
   ```json
   {
     "delay_between_batches": 20
   }
   ```

2. **Reduce concurrent downloads**:
   ```json
   {
     "max_concurrent": 1
   }
   ```

3. **Use free account settings**:
   ```json
   {
     "account_type": "free"
   }
   ```

### Connection Issues
**Problem**: Cannot connect to Telegram servers

**Solutions**:
1. Check internet connection
2. Verify API credentials
3. Try different session name
4. Use VPN if blocked

### Large Files
**Problem**: Files too large to download

**Solutions**:
1. **Ignore size limits**:
   ```json
   {
     "ignore_file_size_limit": true
   }
   ```

2. **Increase size limit**:
   ```json
   {
     "max_file_size_mb": 100
   }
   ```

3. **Use premium account** for larger limits

### Memory Issues
**Problem**: High memory usage during downloads

**Solutions**:
1. **Reduce batch size**:
   ```json
   {
     "batch_size": 5
   }
   ```

2. **Enable cleanup**:
   ```json
   {
     "auto_cleanup": true
   }
   ```

3. **Monitor memory usage** in logs

## Performance Tips

### For Free Accounts
- Use 1 concurrent download
- Set 15-20 second delays
- Keep batch size at 5
- Avoid peak hours

### For Premium Accounts
- Use 3-5 concurrent downloads
- Set 8-10 second delays
- Increase batch size to 8-10
- Can handle larger files

### General Tips
- **Start slow**: Begin with conservative settings
- **Monitor logs**: Check for errors and warnings
- **Resume safely**: Don't delete state files
- **Backup important**: Keep copies of config files

## Rate Limiting Guidelines

### Free Account Limits
| Setting | Recommended Value | Notes |
|---------|-------------------|-------|
| Max Concurrent | 1 | Single file at a time |
| Delay | 15-20 seconds | Longer delays |
| Batch Size | 5 | Small batches |
| File Size | 10MB | Conservative limit |

### Premium Account Limits
| Setting | Recommended Value | Notes |
|---------|-------------------|-------|
| Max Concurrent | 3-5 | Multiple files |
| Delay | 8-10 seconds | Moderate delays |
| Batch Size | 8-10 | Larger batches |
| File Size | 100MB+ | Higher limits |

## Troubleshooting Checklist

### Before Starting
- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] API credentials obtained
- [ ] Target channel accessible
- [ ] Sufficient disk space

### During Download
- [ ] Monitor log files
- [ ] Check for errors
- [ ] Verify file downloads
- [ ] Monitor memory usage
- [ ] Check network stability

### After Download
- [ ] Verify file organization
- [ ] Check file integrity
- [ ] Review download statistics
- [ ] Backup important files
- [ ] Clean up temporary files

## Need Help?

### Documentation
- **README.md**: Complete project documentation
- **CHANGELOG.md**: Version history and updates
- **CONTRIBUTING.md**: How to contribute

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share tips
- **Security Issues**: Report privately for sensitive issues

### Quick Commands
```bash
# Check Python version
python3 --version

# Test installation
python3 -c "import telethon"

# Run tests
python3 test_downloader.py

# Check configuration
python3 -c "import json; print(json.dumps(json.load(open('config.json')), indent=2))"
```

---

**Happy Downloading! 🚀**

For more information, visit the [main documentation](README.md) or [report issues](https://github.com/1BitCode-Com/telegram-media-downloader/issues). 
