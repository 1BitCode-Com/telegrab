#!/usr/bin/env python3
"""
Telegram Media Downloader
A comprehensive script to download media from Telegram groups/channels
with support for resuming downloads and handling large numbers of files.
"""

import os
import sys
import json
import time
import argparse
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import base64

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
except ImportError:
    print("Telethon not found. Installing...")
    os.system("pip install telethon")
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
    from telethon.errors import FloodWaitError, SessionPasswordNeededError

# Configuration
DEFAULT_CONFIG = {
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
    "allowed_extensions": ["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "pdf", "doc", "docx"],
    "media_types": ["photo", "video", "document"],
    "create_date_folders": True,
    "resume_downloads": True,
    "concurrent_downloads": True,
    "max_concurrent": 3,
    "auto_cleanup": False,
    "cleanup_temp_files": True,
    "cleanup_interval_hours": 24
}

class StateManager:
    """Manages download state and progress tracking"""
    
    def __init__(self, state_file: str, encryption_key: str = None):
        self.state_file = state_file
        self.encryption_key = encryption_key
        self.state = self.load_state()
    
    def _get_fernet(self):
        """Get Fernet instance for encryption"""
        if not CRYPTO_AVAILABLE or not self.encryption_key:
            return None
        
        try:
            salt = b'telegram_downloader_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            return Fernet(key)
        except Exception as e:
            logging.warning(f"Failed to initialize encryption: {e}")
            return None
    
    def load_state(self) -> Dict[str, Any]:
        """Load download state from JSON file"""
        try:
            if os.path.exists(self.state_file):
                fernet = self._get_fernet()
                
                if fernet:
                    # Load encrypted state
                    with open(self.state_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = fernet.decrypt(encrypted_data)
                    return json.loads(decrypted_data.decode())
                else:
                    # Load plain state
                    with open(self.state_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            logging.error(f"Error loading state: {e}")
        return {"last_message_id": 0, "downloaded_files": [], "total_downloaded": 0}
    
    def save_state(self, last_message_id: int, downloaded_files: List[str]):
        """Save current download state"""
        try:
            state = {
                "last_message_id": last_message_id,
                "downloaded_files": downloaded_files,
                "total_downloaded": len(downloaded_files),
                "last_updated": datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            fernet = self._get_fernet()
            
            if fernet:
                # Save encrypted state
                json_data = json.dumps(state, indent=2, ensure_ascii=False)
                encrypted_data = fernet.encrypt(json_data.encode())
                with open(self.state_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # Save plain state
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

class FileOrganizer:
    """Organizes downloaded files into folders"""
    
    def __init__(self, download_dir: str, create_date_folders: bool = True):
        self.download_dir = Path(download_dir)
        self.create_date_folders = create_date_folders
        self.download_dir.mkdir(exist_ok=True)
    
    def get_file_path(self, message_date: datetime, filename: str) -> Path:
        """Get organized file path based on date"""
        if self.create_date_folders:
            date_folder = message_date.strftime("%Y-%m")
            file_path = self.download_dir / date_folder / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = self.download_dir / filename
        
        return file_path
    
    def generate_unique_filename(self, file_path: Path) -> Path:
        """Generate unique filename if file exists"""
        if not file_path.exists():
            return file_path
        
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_path = file_path.parent / new_filename
            if not new_path.exists():
                return new_path
            counter += 1

class ProgressTracker:
    """Tracks download progress and statistics"""
    
    def __init__(self):
        self.total_files = 0
        self.downloaded_files = 0
        self.failed_downloads = 0
        self.start_time = None
        self.file_sizes = []
        self.concurrent_downloads = 0
        self.max_concurrent = 0
        self.downloaded_file_list = []
        self.memory_usage = 0
    
    def start(self):
        """Start tracking"""
        self.start_time = datetime.now()
    
    def update(self, success: bool, file_size: int = 0, filename: str = "", file_path: str = ""):
        """Update progress"""
        if success:
            self.downloaded_files += 1
            if file_size > 0:
                self.file_sizes.append(file_size)
            if filename and file_path:
                self.downloaded_file_list.append({
                    'filename': filename,
                    'file_path': file_path,
                    'file_size_mb': file_size / (1024 * 1024),
                    'download_time': datetime.now().isoformat()
                })
        else:
            self.failed_downloads += 1
    
    def set_concurrent_info(self, current: int, max_concurrent: int):
        """Set concurrent download information"""
        self.concurrent_downloads = current
        self.max_concurrent = max_concurrent
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    def check_memory_limit(self, limit_mb: float = 1000) -> bool:
        """Check if memory usage exceeds limit"""
        current_memory = self.get_memory_usage()
        self.memory_usage = current_memory
        
        if current_memory > limit_mb:
            logging.warning(f"Memory usage high: {current_memory:.1f}MB (limit: {limit_mb}MB)")
            return False
        return True
    
    def export_to_csv(self, filename: str = "download_report.csv"):
        """Export download statistics to CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['filename', 'file_path', 'file_size_mb', 'download_time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for file_info in self.downloaded_file_list:
                    writer.writerow(file_info)
            
            logging.info(f"Download report exported to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error exporting CSV: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        if not self.start_time:
            return {}
        
        elapsed = datetime.now() - self.start_time
        total_size = sum(self.file_sizes)
        
        return {
            "total_files": self.total_files,
            "downloaded": self.downloaded_files,
            "failed": self.failed_downloads,
            "success_rate": (self.downloaded_files / max(self.total_files, 1)) * 100,
            "elapsed_time": str(elapsed),
            "total_size_mb": total_size / (1024 * 1024),
            "avg_speed_mbps": (total_size / (1024 * 1024)) / max(elapsed.total_seconds(), 1),
            "concurrent_downloads": f"{self.concurrent_downloads}/{self.max_concurrent}",
            "memory_usage_mb": self.memory_usage
        }

class TelegramMediaDownloader:
    """Main downloader class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.state_manager = StateManager(config["state_file"], config.get("encryption_key"))
        self.file_organizer = FileOrganizer(config["download_dir"], config["create_date_folders"])
        self.progress_tracker = ProgressTracker()
        self.download_queue = asyncio.Queue()
        
        # Setup logging
        self.setup_logging()
        
        # Adjust settings for account type BEFORE creating semaphore
        self.adjust_settings_for_account_type()
        
        # Create semaphore with updated max_concurrent
        self.semaphore = asyncio.Semaphore(self.config.get("max_concurrent", 3))
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.config["log_file"]
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def validate_download_directory(self):
        """Validate and create download directory"""
        download_dir = self.config["download_dir"]
        
        try:
            # Convert to absolute path
            download_dir = os.path.abspath(download_dir)
            self.config["download_dir"] = download_dir
            
            # Check if directory exists
            if not os.path.exists(download_dir):
                logging.info(f"Creating download directory: {download_dir}")
                os.makedirs(download_dir, exist_ok=True)
            
            # Check if directory is writable
            if not os.access(download_dir, os.W_OK):
                raise PermissionError(f"No write permission for directory: {download_dir}")
            
            logging.info(f"Download directory validated: {download_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Error validating download directory: {e}")
            return False
    
    def adjust_settings_for_account_type(self):
        """Adjust settings based on account type (free/premium)"""
        account_type = self.config.get("account_type", "free")
        
        if account_type == "premium":
            premium_settings = self.config.get("premium_settings", {})
            self.config["max_concurrent"] = premium_settings.get("max_concurrent", 50)
            self.config["delay_between_batches"] = premium_settings.get("delay_between_batches", 1)
            self.config["batch_size"] = premium_settings.get("batch_size", 200)
            logging.info("Using Premium account settings (50 concurrent downloads, faster speed)")
        else:
            free_settings = self.config.get("free_settings", {})
            self.config["max_concurrent"] = free_settings.get("max_concurrent", 10)
            self.config["delay_between_batches"] = free_settings.get("delay_between_batches", 3)
            self.config["batch_size"] = free_settings.get("batch_size", 50)
            logging.info("Using Free account settings (10 concurrent downloads, slower speed)")
    
    def cleanup_temp_files(self):
        """Clean up temporary files and old downloads"""
        try:
            download_dir = Path(self.config["download_dir"])
            if not download_dir.exists():
                return
            
            # Clean up temporary files
            temp_patterns = ["*.tmp", "*.temp", "*.part", "*.download"]
            for pattern in temp_patterns:
                for temp_file in download_dir.rglob(pattern):
                    try:
                        temp_file.unlink()
                        logging.info(f"Cleaned up temporary file: {temp_file}")
                    except Exception as e:
                        logging.warning(f"Failed to clean up {temp_file}: {e}")
            
            # Clean up old downloads based on interval
            if self.config.get("auto_cleanup", False):
                cleanup_interval = self.config.get("cleanup_interval_hours", 24)
                cutoff_time = datetime.now().timestamp() - (cleanup_interval * 3600)
                
                for file_path in download_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            if file_path.stat().st_mtime < cutoff_time:
                                file_path.unlink()
                                logging.info(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            logging.warning(f"Failed to clean up {file_path}: {e}")
            
            logging.info("Cleanup completed")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    
    async def initialize_client(self):
        """Initialize Telegram client"""
        try:
            self.client = TelegramClient(
                self.config["session_name"],
                self.config["api_id"],
                self.config["api_hash"]
            )
            await self.client.start()
            logging.info("Telegram client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            raise
    
    def is_valid_media(self, message) -> bool:
        """Check if message contains valid media"""
        if not message.media:
            return False
        
        # Check media type
        if isinstance(message.media, MessageMediaPhoto):
            return "photo" in self.config["media_types"]
        elif isinstance(message.media, MessageMediaDocument):
            return "document" in self.config["media_types"]
        elif isinstance(message.media, MessageMediaWebPage):
            return "webpage" in self.config["media_types"]
        
        return False
    
    def is_valid_file_size(self, file_size: int) -> bool:
        """Check if file size is within limits"""
        # If ignore_file_size_limit is true, skip size check
        if self.config.get("ignore_file_size_limit", False):
            return True
        
        max_size = self.config["max_file_size_mb"] * 1024 * 1024
        return file_size <= max_size
    
    def is_valid_extension(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not self.config["allowed_extensions"]:
            return True
        
        ext = filename.split('.')[-1].lower()
        return ext in self.config["allowed_extensions"]
    
    def is_within_date_range(self, message_date: datetime) -> bool:
        """Check if message date is within specified range"""
        if not hasattr(self, 'start_date') and not hasattr(self, 'end_date'):
            return True
        
        if hasattr(self, 'start_date') and message_date < self.start_date:
            return False
        
        if hasattr(self, 'end_date') and message_date > self.end_date:
            return False
        
        return True
    
    async def download_media_concurrent(self, message, target_entity) -> bool:
        """Download media from a single message with concurrency control"""
        async with self.semaphore:
            return await self.download_media(message, target_entity)
    
    async def download_media(self, message, target_entity) -> bool:
        """Download media from a single message"""
        try:
            if not self.is_valid_media(message):
                return False
            
            # Get file info
            if hasattr(message.media, 'document'):
                file_size = message.media.document.size
                filename = message.media.document.attributes[0].file_name
            elif hasattr(message.media, 'photo'):
                file_size = message.media.photo.sizes[-1].size
                filename = f"photo_{message.id}.jpg"
            else:
                return False
            
            # Check file size and extension
            if not self.is_valid_file_size(file_size):
                logging.info(f"Skipping {filename} - file too large ({file_size / (1024*1024):.1f}MB)")
                return False
            
            if not self.is_valid_extension(filename):
                logging.info(f"Skipping {filename} - extension not allowed")
                return False
            
            # Generate file path
            file_path = self.file_organizer.get_file_path(message.date, filename)
            file_path = self.file_organizer.generate_unique_filename(file_path)
            
            # Download file
            logging.info(f"Downloading: {filename}")
            await self.client.download_media(message.media, str(file_path))
            
            # Update progress
            self.progress_tracker.update(True, file_size, filename, str(file_path))
            logging.info(f"Successfully downloaded: {filename}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error downloading media from message {message.id}: {e}")
            self.progress_tracker.update(False)
            return False
    
    async def download_from_entity(self, target: str):
        """Download all media from target entity"""
        try:
            # Validate download directory first
            if not self.validate_download_directory():
                raise Exception("Failed to validate download directory")
            
            # Get entity with password if provided
            try:
                entity = await self.client.get_entity(target)
            except Exception as e:
                if "password" in str(e).lower() and hasattr(self, 'password'):
                    logging.info("Channel requires password, attempting with provided password...")
                    entity = await self.client.get_entity(target, password=self.password)
                else:
                    raise e
            
            logging.info(f"Starting download from: {entity.title}")
            logging.info(f"Files will be saved to: {self.config['download_dir']}")
            
            # Set date filters if provided
            if hasattr(self, 'start_date'):
                logging.info(f"Filtering from date: {self.start_date}")
            if hasattr(self, 'end_date'):
                logging.info(f"Filtering to date: {self.end_date}")
            
            # Get last message ID for resume
            last_id = 0
            if self.config["resume_downloads"]:
                last_id = self.state_manager.state.get("last_message_id", 0)
                if last_id > 0:
                    logging.info(f"Resuming from message ID: {last_id}")
            
            # Initialize progress tracker
            self.progress_tracker.start()
            self.progress_tracker.set_concurrent_info(0, self.config.get("max_concurrent", 3))
            
            # Download messages in batches
            batch_count = 0
            downloaded_files = []
            
            # Collect messages for batch processing
            messages_to_download = []
            
            async for message in self.client.iter_messages(
                entity, 
                reverse=True, 
                offset_id=last_id
            ):
                batch_count += 1
                
                # Check date filter
                if not self.is_within_date_range(message.date):
                    continue
                
                if self.is_valid_media(message):
                    messages_to_download.append(message)
                
                # Process batch when full or at end
                if len(messages_to_download) >= self.config["batch_size"] or batch_count % self.config["batch_size"] == 0:
                    if messages_to_download:
                        # Download messages concurrently
                        tasks = []
                        for msg in messages_to_download:
                            if self.config.get("concurrent_downloads", True):
                                task = self.download_media_concurrent(msg, entity)
                            else:
                                task = self.download_media(msg, entity)
                            tasks.append(task)
                        
                        # Wait for all downloads in batch to complete
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Process results
                        for i, result in enumerate(results):
                            if isinstance(result, Exception):
                                logging.error(f"Download failed: {result}")
                            elif result:
                                downloaded_files.append(messages_to_download[i].id)
                        
                        # Update concurrent info
                        self.progress_tracker.set_concurrent_info(len(tasks), self.config.get("max_concurrent", 3))
                        
                        # Clear batch
                        messages_to_download = []
                    
                    # Save state periodically
                    if batch_count % self.config["batch_size"] == 0:
                        self.state_manager.save_state(message.id, downloaded_files)
                        logging.info(f"Batch {batch_count // self.config['batch_size']} completed")
                        
                        # Add delay to avoid rate limiting
                        await asyncio.sleep(self.config["delay_between_batches"])
                
                # Update progress
                self.progress_tracker.total_files += 1
                
                # Check memory usage
                if not self.progress_tracker.check_memory_limit(1000):  # 1GB limit
                    logging.warning("Memory usage high, pausing for cleanup...")
                    await asyncio.sleep(5)  # Pause for 5 seconds
                
                # Print progress every 50 files
                if batch_count % 50 == 0:
                    stats = self.progress_tracker.get_stats()
                    logging.info(f"Progress: {stats['downloaded']}/{stats['total_files']} files downloaded")
                    logging.info(f"Memory usage: {stats['memory_usage_mb']:.1f}MB")
            
            # Process remaining messages
            if messages_to_download:
                tasks = []
                for msg in messages_to_download:
                    if self.config.get("concurrent_downloads", True):
                        task = self.download_media_concurrent(msg, entity)
                    else:
                        task = self.download_media(msg, entity)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logging.error(f"Download failed: {result}")
                    elif result:
                        downloaded_files.append(messages_to_download[i].id)
            
            # Final state save
            self.state_manager.save_state(0, downloaded_files)
            
            # Print final statistics
            final_stats = self.progress_tracker.get_stats()
            logging.info("Download completed!")
            logging.info(f"Final statistics: {final_stats}")
            
            # Export CSV if requested
            if self.config.get("csv_export", False):
                self.progress_tracker.export_to_csv()
            
            # Perform cleanup if enabled
            if self.config.get("auto_cleanup", False):
                self.cleanup_temp_files()
            
        except Exception as e:
            logging.error(f"Error during download: {e}")
            raise

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration from file"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG.copy()
        # Save default config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config

def save_api_credentials(api_id: str, api_hash: str, config_file: str = "config.json"):
    """Save API credentials to config file"""
    config = load_config(config_file)
    config["api_id"] = api_id
    config["api_hash"] = api_hash
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"API credentials saved to {config_file}")

def get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Telegram Media Downloader")
    parser.add_argument("--target", help="Target group/channel link or username")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--api-id", help="Telegram API ID")
    parser.add_argument("--api-hash", help="Telegram API Hash")
    parser.add_argument("--download-dir", help="Download directory path")
    parser.add_argument("--save-credentials", action="store_true", help="Save API credentials to config file")
    parser.add_argument("--setup", action="store_true", help="Interactive setup mode")
    parser.add_argument("--max-concurrent", type=int, help="Maximum concurrent downloads")
    parser.add_argument("--no-concurrent", action="store_true", help="Disable concurrent downloads")
    parser.add_argument("--start-date", help="Start date for filtering (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for filtering (YYYY-MM-DD)")
    parser.add_argument("--password", help="Password for protected channels")
    parser.add_argument("--csv-export", action="store_true", help="Export download statistics to CSV")
    parser.add_argument("--cleanup", action="store_true", help="Enable automatic cleanup of downloaded files")
    parser.add_argument("--account-type", choices=["free", "premium"], help="Telegram account type (free/premium)")
    parser.add_argument("--ignore-size-limit", action="store_true", help="Ignore file size limits")
    
    args = parser.parse_args()
    
    # Interactive setup mode
    if args.setup:
        print("Telegram Media Downloader - Interactive Setup")
        print("=" * 50)
        
        # Get API credentials
        api_id = get_user_input("Enter your Telegram API ID")
        api_hash = get_user_input("Enter your Telegram API Hash")
        
        if not api_id or not api_hash:
            print("Error: API ID and API Hash are required!")
            sys.exit(1)
        
        # Get download directory
        download_dir = get_user_input("Enter download directory path", "downloads")
        
        # Get concurrent settings
        max_concurrent = get_user_input("Enter maximum concurrent downloads", "3")
        try:
            max_concurrent = int(max_concurrent)
        except ValueError:
            max_concurrent = 3
        
        # Get cleanup settings
        cleanup_enabled = get_user_input("Enable automatic cleanup of downloaded files? (y/N)", "N").lower() == "y"
        cleanup_interval = get_user_input("Enter cleanup interval in hours (default 24)", "24")
        try:
            cleanup_interval = int(cleanup_interval)
        except ValueError:
            cleanup_interval = 24
        
        # Save credentials if requested
        if args.save_credentials:
            save_api_credentials(api_id, api_hash, args.config)
        
        # Get target
        target = get_user_input("Enter target group/channel link or username")
        if not target:
            print("Error: Target is required!")
            sys.exit(1)
        
        # Update config
        config = load_config(args.config)
        config["api_id"] = api_id
        config["api_hash"] = api_hash
        config["download_dir"] = download_dir
        config["max_concurrent"] = max_concurrent
        config["concurrent_downloads"] = not args.no_concurrent
        config["csv_export"] = args.csv_export
        config["auto_cleanup"] = cleanup_enabled
        config["cleanup_interval_hours"] = cleanup_interval
        
        with open(args.config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to {args.config}")
        
        # Start download
        downloader = TelegramMediaDownloader(config)
        try:
            await downloader.initialize_client()
            await downloader.download_from_entity(target)
        except KeyboardInterrupt:
            logging.info("Download interrupted by user")
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            sys.exit(1)
        finally:
            if downloader.client:
                await downloader.client.disconnect()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.api_id:
        config["api_id"] = args.api_id
    if args.api_hash:
        config["api_hash"] = args.api_hash
    if args.download_dir:
        config["download_dir"] = args.download_dir
    if args.max_concurrent:
        config["max_concurrent"] = args.max_concurrent
    if args.no_concurrent:
        config["concurrent_downloads"] = False
    if args.csv_export:
        config["csv_export"] = True
    if args.cleanup:
        config["auto_cleanup"] = True
        config["cleanup_interval_hours"] = args.cleanup_interval_hours
    if args.ignore_size_limit:
        config["ignore_file_size_limit"] = True
    
    # Save credentials if requested
    if args.save_credentials and args.api_id and args.api_hash:
        save_api_credentials(args.api_id, args.api_hash, args.config)
    
    # Validate required fields
    if not config["api_id"] or not config["api_hash"]:
        print("Error: API ID and API Hash are required!")
        print("Please set them in config.json or use --api-id and --api-hash arguments")
        print("Or use --setup for interactive setup")
        sys.exit(1)
    
    if not args.target:
        print("Error: Target is required!")
        print("Please provide --target argument or use --setup for interactive mode")
        sys.exit(1)
    
    # Create downloader and start
    downloader = TelegramMediaDownloader(config)
    
    # Parse date filters
    if args.start_date:
        try:
            downloader.start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("Error: Invalid start date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    if args.end_date:
        try:
            downloader.end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("Error: Invalid end date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Set password if provided
    if args.password:
        downloader.password = args.password
    
    # Adjust settings based on account type
    if args.account_type:
        downloader.config["account_type"] = args.account_type
    downloader.adjust_settings_for_account_type()
    
    try:
        await downloader.initialize_client()
        await downloader.download_from_entity(args.target)
    except KeyboardInterrupt:
        logging.info("Download interrupted by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if downloader.client:
            await downloader.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 