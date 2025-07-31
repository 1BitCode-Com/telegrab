#!/usr/bin/env python3
"""
Quick Start Guide for Telegram Media Downloader
A simple script to help users get started quickly
"""

import os
import sys
import json
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"Python {sys.version.split()[0]} - Compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import telethon
        print("Telethon library - Installed")
        return True
    except ImportError:
        print("Telethon library - Not installed")
        print("Installing Telethon...")
        subprocess.run([sys.executable, "-m", "pip", "install", "telethon"])
        try:
            import telethon
            print("Telethon library - Installed successfully")
            return True
        except ImportError:
            print("Failed to install Telethon")
            return False

def setup_config():
    """Setup basic configuration"""
    print("\nCONFIGURATION SETUP")
    print("-" * 30)
    
    if os.path.exists("config.json"):
        print("Configuration file found")
        with open("config.json", "r") as f:
            config = json.load(f)
        
        if config.get("api_id") and config.get("api_hash"):
            print("API credentials found")
            return True
        else:
            print("API credentials missing")
    else:
        print("Configuration file not found")
    
    print("\nSETTING UP API CREDENTIALS")
    print("1. Open your web browser to get API credentials")
    print("2. Log in with your phone number")
    print("3. Create a new application")
    print("4. Copy the API ID and API Hash")
    
    open_browser = input("\nOpen browser to get API credentials? (y/n): ").lower().strip()
    if open_browser == 'y':
        import webbrowser
        webbrowser.open("https://my.telegram.org/")
    
    print("\nPlease enter your API credentials:")
    api_id = input("API ID: ").strip()
    api_hash = input("API Hash: ").strip()
    
    if not api_id or not api_hash:
        print("Error: API credentials are required!")
        return False
    
    config = {
        "api_id": api_id,
        "api_hash": api_hash,
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
        "create_date_folders": True,
        "resume_downloads": True
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Configuration saved successfully")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["downloads", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def show_usage_examples():
    """Show usage examples"""
    print("\nUSAGE EXAMPLES")
    print("-" * 20)
    
    examples = [
        ("Download from public group", "python telegram_media_downloader.py --target 'https://t.me/groupname'"),
        ("Download from private group", "python telegram_media_downloader.py --target '@privategroup'"),
        ("Interactive mode", "python run.py"),
        ("Setup mode", "python telegram_media_downloader.py --setup"),
        ("Custom download directory", "python telegram_media_downloader.py --target 'group' --download-dir '/path/to/downloads'"),
        ("Save API credentials", "python telegram_media_downloader.py --api-id '12345' --api-hash 'hash' --save-credentials"),
        ("Test installation", "python test_downloader.py"),
        ("Download only photos", "Edit config.json: set 'media_types': ['photo']"),
        ("Limit file size to 10MB", "Edit config.json: set 'max_file_size_mb': 10")
    ]
    
    for i, (description, command) in enumerate(examples, 1):
        print(f"{i}. {description}")
        print(f"   {command}")
        print()

def main():
    """Main function"""
    print("=" * 60)
    print("    TELEGRAM MEDIA DOWNLOADER - QUICK START")
    print("=" * 60)
    print()
    
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    print("\nCREATING DIRECTORIES")
    print("-" * 25)
    create_directories()
    
    if not setup_config():
        print("\nSetup failed. Please check your API credentials.")
        return
    
    show_usage_examples()
    
    print("SETUP COMPLETED!")
    print("=" * 30)
    print("You can now use the Telegram Media Downloader!")
    print("\nNext steps:")
    print("1. Run: python run.py (interactive mode)")
    print("2. Or run: python telegram_media_downloader.py --setup (setup mode)")
    print("3. Or run: python telegram_media_downloader.py --target 'YOUR_GROUP_LINK'")
    print("4. Check README.md for more information")

if __name__ == "__main__":
    main() 