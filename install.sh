#!/bin/bash

# Telegram Media Downloader Installation Script

echo "Telegram Media Downloader - Installation Script"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7 or higher is required!"
    echo "Current version: $python_version"
    exit 1
fi

echo "Python $python_version found"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x telegram_media_downloader.py
chmod +x run.py
chmod +x test_downloader.py

echo "Scripts made executable"

# Create necessary directories
mkdir -p downloads
mkdir -p logs

echo "Directories created"

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "Creating default config.json..."
    cat > config.json << EOF
{
  "api_id": "",
  "api_hash": "",
  "session_name": "telegram_downloader",
  "download_dir": "downloads",
  "state_file": "download_state.json",
  "log_file": "logs/downloader.log",
  "max_workers": 5,
  "batch_size": 100,
  "delay_between_batches": 2,
  "max_file_size_mb": 100,
  "allowed_extensions": ["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "pdf", "doc", "docx", "txt", "sql", "csv", "json", "xml"],
  "media_types": ["photo", "video", "document"],
  "create_date_folders": true,
  "resume_downloads": true
}
EOF
    echo "Default config.json created"
else
    echo "config.json already exists"
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Get your Telegram API credentials from https://my.telegram.org/"
echo "2. Run the downloader using one of these methods:"
echo ""
echo "   Method 1 - Interactive Setup (Recommended):"
echo "   python3 run.py"
echo ""
echo "   Method 2 - Setup Mode:"
echo "   python3 telegram_media_downloader.py --setup"
echo ""
echo "   Method 3 - Command Line:"
echo "   python3 telegram_media_downloader.py --target 'https://t.me/groupname'"
echo ""
echo "   Method 4 - Custom Directory:"
echo "   python3 telegram_media_downloader.py --target 'group' --download-dir '/path/to/downloads'"
echo ""
echo "   Method 5 - Save API Credentials:"
echo "   python3 telegram_media_downloader.py --api-id 'YOUR_ID' --api-hash 'YOUR_HASH' --save-credentials"
echo ""
echo "3. Test installation:"
echo "   python3 test_downloader.py"
echo ""
echo "For more information, see README.md" 