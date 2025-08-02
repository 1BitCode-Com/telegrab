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
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import base64

try:
    from tqdm.auto import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

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

# Custom logging handler for tqdm compatibility
class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg, file=sys.stderr)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

# Configuration
DEFAULT_CONFIG = {
    "api_id": "",
    "api_hash": "",
    "session_name": "telegram_downloader",
    "download_dir": "downloads",
    "state_file": "download_state.json",
    "log_file": "logs/downloader.log",
    "create_date_folders": True,
    "resume_downloads": True,
    "auto_cleanup": False,
    "cleanup_temp_files": True,
    "cleanup_interval_hours": 24,
    "overwrite_existing_files": False,
    "rate_limit_delay": 5,
    "chunk_size_kb": 256,
    "chunk_delay_ms": 100,
    "account_type": "free",
    "free_settings": {
        "max_concurrent": 1,
        "delay_between_batches": 15,
        "batch_size": 5
    },
    "premium_settings": {
        "max_concurrent": 3,
        "delay_between_batches": 8,
        "batch_size": 8
    }
}

class StateManager:
    """Manages download state and progress tracking"""
    
    def __init__(self, state_file: str, encryption_key: str = None):
        self.state_file = state_file
        self.encryption_key = encryption_key
        self._lock = asyncio.Lock()
        self.state = self.load_state()
        if "downloaded_files" not in self.state or not isinstance(self.state.get("downloaded_files"), list):
            self.state["downloaded_files"] = []
    
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
    
    def _save_state_to_disk(self):
        """Saves the current state to the disk."""
        try:
            # Ensure state file directory exists
            state_dir = os.path.dirname(self.state_file)
            if state_dir:
                os.makedirs(state_dir, exist_ok=True)
            
            fernet = self._get_fernet()
            
            if fernet:
                json_data = json.dumps(self.state, indent=2, ensure_ascii=False)
                encrypted_data = fernet.encrypt(json_data.encode())
                with open(self.state_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    async def record_download(self, message_id: int, file_path: str):
        """Records a successful download and updates the state."""
        async with self._lock:
            self.state["downloaded_files"].append(file_path)
            self.state["total_downloaded"] = len(self.state["downloaded_files"])
            
            current_last_id = self.state.get("last_message_id", 0)
            self.state["last_message_id"] = max(current_last_id, message_id)
            
            self.state["last_updated"] = datetime.now().isoformat()
            self._save_state_to_disk()

class FileOrganizer:
    """Organizes downloaded files into folders"""
    
    def __init__(self, download_dir: str, create_date_folders: bool = True, config: Dict[str, Any] = None):
        self.download_dir = Path(download_dir)
        self.create_date_folders = create_date_folders
        self.config = config or {}
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
        
        # Check if we should overwrite existing files
        if self.config.get("overwrite_existing_files", False):
            logging.debug(f"Overwriting existing file: {file_path}")
            return file_path
        
        # Generate unique filename
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
        self.file_organizer = FileOrganizer(config["download_dir"], config["create_date_folders"], config)
        self.progress_tracker = ProgressTracker()
        self.download_queue = asyncio.Queue()
        self.last_saved_id = 0
        self.setup_logging()
        
        # Setup logging first
        # self.setup_logging() # This line is now redundant as setup_logging is called in __init__
        
        # Initialize user agents
        self.user_agents = config.get("user_agents", [
            "Telegram/8.4.2 (Android 11; SDK 30)",
            "Telegram/8.5.1 (iOS 15.0; iPhone)",
            "Telegram/8.6.0 (Windows 10; x64)",
            "Telegram/8.3.1 (macOS 12.0; x64)",
            "Telegram/8.7.0 (Linux; x64)"
        ])
        self.request_count = 0
        self._download_lock = asyncio.Lock()
        self._last_download_start_time = 0
        self.current_entity = None
        
        # self.adjust_settings_for_account_type() # This is now handled by directly reading from config
        self.adjust_settings_for_account_type()
        
        # Initialize semaphore for concurrent downloads
        self.semaphore = asyncio.Semaphore(self.config.get("max_concurrent", 1))
    
    def setup_logging(self):
        """Setup logging configuration for clean tqdm output."""
        log_file = self.config["log_file"]
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Keep file logging as before
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Use our custom handler for stream output
        tqdm_handler = TqdmLoggingHandler()
        tqdm_handler.setLevel(logging.INFO)
        tqdm_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        tqdm_handler.setFormatter(tqdm_formatter)
        
        # Get root logger and remove existing handlers
        log = logging.getLogger()
        for h in log.handlers[:]:
            log.removeHandler(h)
            h.close()

        log.addHandler(file_handler)
        log.addHandler(tqdm_handler)
        log.setLevel(logging.INFO)
    
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
        
        settings_block = {}
        log_msg = ""
        if account_type == "premium":
            settings_block = self.config.get("premium_settings", {})
            log_msg = "Using Premium account settings"
        else:
            settings_block = self.config.get("free_settings", {})
            log_msg = "Using Free account settings"

        # Update the main config with the specific settings
        self.config.update(settings_block)
        
        logging.info(f"{log_msg} ({self.config.get('max_concurrent')} concurrent, "
                     f"{self.config.get('delay_between_batches')}s delay, "
                     f"batch size {self.config.get('batch_size')})")

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
    
    def is_valid_media(self, message):
        """Check if message media type is allowed"""
        try:
            if not message.media:
                return False
            
            # Check media type
            allowed_types = self.config.get("media_types", ["photo", "video", "document"])
            
            if hasattr(message.media, 'photo') and "photo" in allowed_types:
                return True
            elif hasattr(message.media, 'document') and "document" in allowed_types:
                return True
            elif hasattr(message.media, 'video') and "video" in allowed_types:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Error checking media type: {e}")
            return False

    def get_filename(self, message):
        """Get filename from message"""
        try:
            if hasattr(message.media, 'document'):
                return message.media.document.attributes[0].file_name
            elif hasattr(message.media, 'photo'):
                return f"photo_{message.id}.jpg"
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting filename: {e}")
            return None
    
    async def get_file_size(self, media):
        """Get file size from media"""
        try:
            if hasattr(media, 'document'):
                return media.document.size
            elif hasattr(media, 'photo'):
                return media.photo.sizes[-1].size
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting file size: {e}")
            return None
    
    def change_user_agent(self):
        """Change User Agent randomly"""
        if self.config.get("user_agents_enabled", False) and self.user_agents:
            import random
            new_agent = random.choice(self.user_agents)
            if hasattr(self.client, 'session') and hasattr(self.client.session, 'headers'):
                self.client.session.headers.update({'User-Agent': new_agent})
                logging.info(f"Changed User Agent to: {new_agent}")

    async def worker(self, name: str):
        """Worker to process downloads from the queue."""
        # Add import here to fix the error
        import random
        while True:
            try:
                message_id = await self.download_queue.get()
                
                # Fetch fresh message object to get a valid file reference
                message = await self.client.get_messages(self.current_entity, ids=message_id)
                if not message:
                    logging.warning(f"Worker '{name}' could not find message with ID: {message_id}")
                    self.download_queue.task_done()
                    continue

                logging.debug(f"Worker '{name}' picked up message ID: {message.id}")
                await self.download_media(message)
                self.download_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker '{name}' encountered an error: {e}")
                self.download_queue.task_done()

    async def download_media(self, message) -> bool:
        """Download media from a single message"""
        # Rate limit the start of downloads to avoid flood waits
        async with self._download_lock:
            delay = self.config.get("rate_limit_delay", 5)
            if self._last_download_start_time > 0:
                elapsed = time.time() - self._last_download_start_time
                if elapsed < delay:
                    sleep_for = delay - elapsed
                    logging.debug(f"Rate limiting active. Waiting for {sleep_for:.2f} seconds.")
                    await asyncio.sleep(sleep_for)
            self._last_download_start_time = time.time()

        filename = "unknown_file"
        file_path = None
        try:
            # Increment request count and change user agent if needed
            self.request_count += 1
            if self.config.get("user_agents_enabled", False):
                change_every = self.config.get("change_user_agent_every", 6)
                if self.request_count % change_every == 0:
                    self.change_user_agent()
            
            # Check if message has media
            if not message.media:
                logging.debug(f"Message {message.id} has no media")
                return False
            
            # Check if media type is allowed
            if not self.is_valid_media(message):
                logging.debug(f"Message {message.id} media type not allowed")
                return False
            
            # Get file info
            filename = self.get_filename(message)
            if not filename:
                logging.debug(f"Message {message.id} has no valid filename")
                return False

            file_path = self.file_organizer.get_file_path(message.date, filename)
            file_path = self.file_organizer.generate_unique_filename(file_path)
            
            logging.debug(f"Preparing to download: '{filename}' (ID: {message.id}, Date: {message.date.strftime('%Y-%m-%d')})")
            
            # Add very short delay before download (human-like)
            import random
            pre_download_delay = random.uniform(0.5, 1.5)  # 0.5-1.5 seconds before download
            await asyncio.sleep(pre_download_delay)

            # Manual download with chunking and throttling
            file_size = await self.get_file_size(message.media)
            if not file_size:
                logging.warning(f"Could not determine file size for message {message.id}, skipping download.")
                return False
            
            chunk_size_bytes = self.config.get("chunk_size_kb", 256) * 1024
            chunk_delay_sec = self.config.get("chunk_delay_ms", 100) / 1000.0

            pbar = None
            if TQDM_AVAILABLE:
                pbar = tqdm(
                    total=file_size,
                    desc=filename,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    leave=False,
                    ncols=80,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
                )
            
            try:
                with open(file_path, "wb") as f:
                    async for chunk in self.client.iter_download(message.media, request_size=chunk_size_bytes):
                        f.write(chunk)
                        if pbar:
                            pbar.update(len(chunk))
                        
                        # Throttle after each chunk
                        if chunk_delay_sec > 0:
                            await asyncio.sleep(chunk_delay_sec)
            finally:
                if pbar:
                    pbar.close()

            logging.info(f"Successfully downloaded: '{filename}' (ID: {message.id}, Date: {message.date.strftime('%Y-%m-%d')})")
            self.progress_tracker.update(True, file_size, filename, str(file_path))
            await self.state_manager.record_download(message.id, str(file_path))
            return True

        except Exception as e:
            logging.error(f"Error downloading {filename}: {e}")
            self.progress_tracker.update(False, 0, filename)
            # Cleanup failed (0-byte) files
            if file_path and file_path.exists() and file_path.stat().st_size == 0:
                try:
                    file_path.unlink()
                    logging.info(f"Cleaned up 0-byte file: {file_path}")
                except Exception as cleanup_e:
                    logging.warning(f"Failed to cleanup 0-byte file {file_path}: {cleanup_e}")
            return False
    
    async def download_from_entity(self, target: str):
        """Producer that adds messages to the download queue."""
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
            
            self.current_entity = entity
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
            
            # Create and start workers
            workers = [
                asyncio.create_task(self.worker(f"Worker-{i+1}")) 
                for i in range(self.config.get("max_concurrent", 1))
            ]
            
            logging.info(f"Started {len(workers)} download workers.")

            # Collect messages for batch processing
            
            logging.info("Starting to iterate through messages...")
            message_count = 0
            
            # Use tqdm for overall progress
            total_messages = await self.client.get_messages(entity, limit=0)
            overall_pbar = None
            if TQDM_AVAILABLE and total_messages:
                overall_pbar = tqdm(total=total_messages.total, desc="Processing messages", unit="msg", dynamic_ncols=True)

            last_processed_id = last_id
            
            # Message iteration loop
            async for message in self.client.iter_messages(entity, reverse=True, offset_id=last_id):
                if overall_pbar:
                    overall_pbar.update(1)
                
                message_count += 1
                last_processed_id = message.id
                
                # Add a delay between batches to avoid flood waits
                if message_count > 0 and message_count % self.config["batch_size"] == 0:
                    delay = self.config["delay_between_batches"]
                    logging.debug(f"Batch limit of {self.config['batch_size']} reached, sleeping for {delay} seconds...")
                    await asyncio.sleep(delay)

                # Periodically save the last processed message ID
                if message_count % 250 == 0: 
                    if overall_pbar and self.state_manager.state.get("last_message_id", 0) > 0:
                        overall_pbar.set_postfix_str(f"Last DL ID: {self.state_manager.state['last_message_id']}")

                if self.is_valid_media(message):
                    await self.download_queue.put(message.id)
            
            if overall_pbar:
                overall_pbar.set_postfix_str("Finished iterating messages.")

            logging.info(f"Finished iterating messages. Last scanned ID: {last_processed_id}.")
            
            await self.download_queue.join()

            for w in workers:
                w.cancel()
            
            await asyncio.gather(*workers, return_exceptions=True)

            if overall_pbar:
                overall_pbar.close()

            logging.info("All download tasks completed.")
            
            logging.info(f"Download completed! Processed {message_count} messages total")

            if self.config.get("csv_export", False):
                self.progress_tracker.export_to_csv()

            stats = self.progress_tracker.get_stats()
            logging.info(f"Final statistics: {stats}")
        except Exception as e:
            logging.error(f"Error during download: {e}")
            raise

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration from file, merging with defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, TypeError) as e:
            logging.warning(f"Could not decode config file, using defaults: {e}")
    
    # Save back the merged config to ensure all keys are present
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Could not write to config file: {e}")
        
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
    parser.add_argument("--password", help="Password for protected channels")
    parser.add_argument("--csv-export", action="store_true", help="Export download statistics to CSV")
    parser.add_argument("--account-type", choices=["free", "premium"], help="Telegram account type (free/premium)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files instead of creating unique names")
    
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
    if args.csv_export:
        config["csv_export"] = True
    if args.overwrite:
        config["overwrite_existing_files"] = True
    
    # Save credentials if requested
    if args.save_credentials and args.api_id and args.api_hash:
        save_api_credentials(args.api_id, args.api_hash, args.config)
    
    # Validate required fields
    if not config["api_id"] or not config["api_hash"]:
        print("Error: API ID and API Hash are required!")
        print("Please set them in config.json or use --api-id and --api-hash arguments")
        print("Or use --setup for interactive setup")
        sys.exit(1)
    
    # Get target from command line or config file
    target = args.target
    if not target:
        target = config.get("target_group")
        if not target:
            print("Error: Target is required!")
            print("Please provide --target argument, set target_group in config.json, or use --setup for interactive mode")
            sys.exit(1)
        else:
            print(f"Using target from config.json: {target}")
    
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
    
    # Adjust settings based on account type, allowing CLI to override
    if args.account_type:
        config["account_type"] = args.account_type
    
    downloader.adjust_settings_for_account_type()
    
    # Re-apply CLI args to override account type settings
    if args.max_concurrent:
        config["max_concurrent"] = args.max_concurrent
        downloader.semaphore = asyncio.Semaphore(config["max_concurrent"]) # Re-initialize semaphore

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

if __name__ == "__main__":
    asyncio.run(main()) 
