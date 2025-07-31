#!/usr/bin/env python3
"""
Interactive runner for Telegram Media Downloader
Provides a user-friendly interface for configuring and running downloads
Updated with custom download directory and API credentials saving
"""

import asyncio
import json
import os
import sys
from telegram_media_downloader import TelegramMediaDownloader, load_config, save_api_credentials, get_user_input

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("    TELEGRAM MEDIA DOWNLOADER - INTERACTIVE RUNNER")
    print("=" * 60)
    print()

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
        os.system("pip install telethon")
        try:
            import telethon
            print("Telethon library - Installed successfully")
            return True
        except ImportError:
            print("Failed to install Telethon")
            return False

def validate_directory(path: str) -> bool:
    """Validate if directory path is accessible and writable"""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Check if directory exists
        if not os.path.exists(abs_path):
            print(f"Directory does not exist: {abs_path}")
            create = input("Create directory? (y/n): ").lower().strip()
            if create == 'y':
                os.makedirs(abs_path, exist_ok=True)
                print(f"Created directory: {abs_path}")
            else:
                return False
        
        # Check if directory is writable
        if not os.access(abs_path, os.W_OK):
            print(f"No write permission for directory: {abs_path}")
            return False
        
        print(f"Directory validated: {abs_path}")
        return True
        
    except Exception as e:
        print(f"Error validating directory: {e}")
        return False

def setup_config():
    """Guide user through configuration setup"""
    print("\nCONFIGURATION SETUP")
    print("-" * 30)
    
    # Check if config exists
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
    
    # Get download directory
    print("\nDOWNLOAD DIRECTORY SETUP")
    print("Choose where to save downloaded files:")
    print("1. Default directory (downloads/)")
    print("2. Custom directory")
    print("3. Current directory")
    
    dir_choice = input("Choose option (1-3): ").strip()
    
    if dir_choice == "1":
        download_dir = "downloads"
    elif dir_choice == "2":
        while True:
            download_dir = input("Enter custom directory path: ").strip()
            if not download_dir:
                download_dir = "downloads"
                break
            
            if validate_directory(download_dir):
                break
            else:
                retry = input("Try another path? (y/n): ").lower().strip()
                if retry != 'y':
                    download_dir = "downloads"
                    break
    elif dir_choice == "3":
        download_dir = "."
    else:
        download_dir = "downloads"
    
    # Validate download directory
    if not validate_directory(download_dir):
        print("Error: Could not validate or create download directory. Setup failed.")
        return False
    
    # Create or update config
    max_concurrent = get_user_input("Enter maximum concurrent downloads", "3")
    try:
        max_concurrent = int(max_concurrent)
    except ValueError:
        max_concurrent = 3
    
    # Get account type
    print("\nACCOUNT TYPE SELECTION")
    print("1. Free account (10 concurrent downloads, slower)")
    print("2. Premium account (50 concurrent downloads, faster)")
    account_choice = get_user_input("Choose account type (1-2)", "1")
    
    if account_choice == "2":
        account_type = "premium"
        max_concurrent = 50
    else:
        account_type = "free"
        max_concurrent = 10
    
    # Get cleanup settings
    cleanup_enabled = get_user_input("Enable automatic cleanup of downloaded files? (y/N)", "N").lower() == "y"
    cleanup_interval = get_user_input("Enter cleanup interval in hours (default 24)", "24")
    try:
        cleanup_interval = int(cleanup_interval)
    except ValueError:
        cleanup_interval = 24
    
    # Get file size limit settings
    print("\nFILE SIZE LIMIT SETTINGS")
    print("1. Apply file size limit (skip large files)")
    print("2. Ignore file size limit (download all files)")
    size_limit_choice = get_user_input("Choose option (1-2)", "1")
    
    if size_limit_choice == "2":
        ignore_size_limit = True
        max_file_size = 0
    else:
        ignore_size_limit = False
        max_file_size = get_user_input("Enter maximum file size in MB (default 10)", "10")
        try:
            max_file_size = int(max_file_size)
        except ValueError:
            max_file_size = 10
    
    config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "session_name": "telegram_downloader",
        "download_dir": download_dir,
        "state_file": "download_state.json",
        "log_file": "logs/downloader.log",
        "max_workers": 5,
        "batch_size": 100,
        "delay_between_batches": 2,
        "max_file_size_mb": max_file_size,
        "ignore_file_size_limit": ignore_size_limit,
        "allowed_extensions": ["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "pdf", "doc", "docx", "txt", "sql", "csv", "json", "xml"],
        "media_types": ["photo", "video", "document"],
        "create_date_folders": True,
        "resume_downloads": True,
        "concurrent_downloads": True,
        "max_concurrent": max_concurrent,
        "auto_cleanup": cleanup_enabled,
        "cleanup_interval_hours": cleanup_interval,
        "account_type": account_type,
        "premium_settings": {
            "max_concurrent": 50,
            "delay_between_batches": 1,
            "batch_size": 200
        },
        "free_settings": {
            "max_concurrent": 10,
            "delay_between_batches": 3,
            "batch_size": 50
        }
    }
    
    # Save config
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Save API credentials
    save_api_credentials(api_id, api_hash)
    
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

def get_download_settings():
    """Get download settings from user"""
    print("\nDOWNLOAD SETTINGS")
    print("-" * 20)
    
    # Get target
    target = input("Enter target group/channel link or username: ").strip()
    if not target:
        print("Error: Target is required!")
        return None
    
    # Get download directory
    config = load_config()
    current_dir = config.get("download_dir", "downloads")
    
    print(f"\nCurrent download directory: {current_dir}")
    change_dir = input("Change download directory? (y/n): ").lower().strip()
    
    if change_dir == 'y':
        new_dir = input("Enter new download directory path: ").strip()
        if new_dir:
            config["download_dir"] = new_dir
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            print(f"Download directory updated to: {new_dir}")
    
    return target

async def run_downloader(target: str):
    """Run the downloader with given target"""
    try:
        config = load_config()
        downloader = TelegramMediaDownloader(config)
        
        print(f"\nStarting download from: {target}")
        print("Press Ctrl+C to stop the download")
        
        await downloader.initialize_client()
        await downloader.download_from_entity(target)
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'downloader' in locals() and downloader.client:
            await downloader.client.disconnect()
    
    return True

def main():
    """Main interactive function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    # Setup directories
    print("\nCREATING DIRECTORIES")
    print("-" * 25)
    create_directories()
    
    # Setup configuration
    if not setup_config():
        print("\nSetup failed. Please check your API credentials.")
        return
    
    # Show usage
    show_usage_examples()
    
    print("SETUP COMPLETED!")
    print("=" * 30)
    print("You can now use the Telegram Media Downloader!")
    print("\nNext steps:")
    print("1. Run: python run.py (interactive mode)")
    print("2. Or run: python telegram_media_downloader.py --setup (setup mode)")
    print("3. Or run: python telegram_media_downloader.py --target 'YOUR_GROUP_LINK'")
    print("4. Check README.md for more information")
    
    # Ask if user wants to start download
    start_download = input("\nWould you like to start a download now? (y/n): ").lower().strip()
    if start_download == 'y':
        target = get_download_settings()
        if target:
            asyncio.run(run_downloader(target))
    
    # Ask if user wants to test
    test = input("\nWould you like to test the installation? (y/n): ").lower().strip()
    if test == 'y':
        print("\nRunning test...")
        os.system("python test_downloader.py")

if __name__ == "__main__":
    main() 