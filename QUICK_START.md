# Quick Start Guide

A comprehensive guide to get you started with Telegram Media Downloader v2.0 quickly and efficiently.

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
- **Target group/channel configuration**
- Account type configuration
- File size limit settings

### Method 2: Manual Configuration
1. Edit `config.json` and add your API credentials and target group:
```json
{
  "api_id": "YOUR_API_ID",
  "api_hash": "YOUR_API_HASH",
  "session_name": "telegram_downloader",
  "target_group": "https://t.me/example_channel"
}
```

2. Run the script:
```bash
# This will use the "premium" account settings by default
python3 telegram_media_downloader.py

# To use free account settings, set it in the config or use the CLI argument
python3 telegram_media_downloader.py --account-type "free"
```

## Key Configuration Options

The script is optimized out-of-the-box, but you can fine-tune its performance in `config.json`.

```json
{
    "account_type": "premium",
    "chunk_delay_ms": 200,

    "premium_settings": {
        "max_concurrent": 10
    }
}
```

- `account_type`: Switches between `"premium"` and `"free"` settings blocks.
- `max_concurrent`: The number of files to download at the same time.
- `chunk_delay_ms`: The delay *after* downloading each small piece of a file. **This is the most important setting for avoiding errors.** Increase it if you see `FloodWait` errors.

## Common Issues & Solutions

### `FloodWaitError` or `GetFileRequest` Errors

**Problem**: Telegram is temporarily blocking you for making too many requests.

**Solutions**:
1. **Increase `chunk_delay_ms`**: This is the best solution. Open `config.json` and change `200` to a higher value like `500` or `1000`.
2. **Reduce `max_concurrent`**: Lower the number of parallel downloads.
3. **Use free account settings**: Run the script with `--account-type "free"`.

### `File reference has expired` Errors

**Problem**: The temporary download link expired.
**Solution**: This is fixed automatically in version 2.0. If you see this error, you are likely running an older version of the script.

### Files are 0 bytes

**Problem**: The download failed, leaving an empty file.
**Solution**: This is fixed automatically in version 2.0. The script will now clean up these empty files.

## Need Help?

- **README.md**: For complete project documentation.
- **CHANGELOG.md**: To see what's new in the latest version.
- **GitHub Issues**: Report bugs and request new features.

---

**Happy Downloading! 🚀**

For more information, visit the [main documentation](README.md). 
