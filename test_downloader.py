#!/usr/bin/env python3
"""
Test script for Telegram Media Downloader
This script helps verify the configuration and basic functionality
"""

import asyncio
import json
import os
import sys
from telegram_media_downloader import TelegramMediaDownloader, load_config

async def test_connection():
    """Test Telegram connection and configuration"""
    print("Testing Telegram Media Downloader Configuration...")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_config()
        print("Configuration loaded successfully")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False
    
    # Check required fields
    if not config.get("api_id") or not config.get("api_hash"):
        print("API ID and API Hash are required!")
        print("Please set them in config.json or use command line arguments")
        return False
    
    print("API credentials found")
    
    # Test client initialization
    try:
        downloader = TelegramMediaDownloader(config)
        await downloader.initialize_client()
        print("Telegram client initialized successfully")
        
        # Test getting user info
        me = await downloader.client.get_me()
        print(f"Connected as: {me.first_name} (@{me.username})")
        
        await downloader.client.disconnect()
        print("Client disconnected successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing client: {e}")
        return False

async def test_config_validation():
    """Test configuration validation"""
    print("\nTesting Configuration Validation...")
    print("=" * 50)
    
    # Test with invalid config
    invalid_config = {
        "api_id": "",
        "api_hash": "",
        "max_file_size_mb": -1,
        "batch_size": 0
    }
    
    try:
        downloader = TelegramMediaDownloader(invalid_config)
        print("Should have failed with invalid config")
        return False
    except Exception:
        print("Invalid configuration properly rejected")
    
    return True

def test_file_operations():
    """Test file operations"""
    print("\nTesting File Operations...")
    print("=" * 50)
    
    # Test directory creation
    test_dir = "test_downloads"
    if os.path.exists(test_dir):
        os.system(f"rm -rf {test_dir}")
    
    os.makedirs(test_dir, exist_ok=True)
    print("Test directory created")
    
    # Test config file creation
    test_config = "test_config.json"
    if os.path.exists(test_config):
        os.remove(test_config)
    
    config = load_config(test_config)
    if os.path.exists(test_config):
        print("Default config file created")
        os.remove(test_config)
    else:
        print("Default config file not created")
        return False
    
    # Cleanup
    os.system(f"rm -rf {test_dir}")
    print("Test cleanup completed")
    
    return True

async def main():
    """Main test function"""
    print("Telegram Media Downloader - Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_operations(),
        await test_config_validation(),
        await test_connection()
    ]
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    passed = sum(tests)
    total = len(tests)
    
    for i, result in enumerate(tests, 1):
        status = "PASS" if result else "FAIL"
        print(f"Test {i}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The downloader is ready to use.")
        return 0
    else:
        print("Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 