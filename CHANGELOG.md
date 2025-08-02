# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-08-02

### Added
- **Robust Chunk-Based Downloading**: Implemented a manual, chunk-by-chunk downloading mechanism with configurable delays (`chunk_delay_ms`) to prevent `GetFileRequest` flood waits and ensure stable parallel downloads.
- **Just-in-Time File Reference Fetching**: Workers now fetch fresh message data just before downloading to completely resolve `File reference has expired` errors.
- **Smart State Management**: The download state now accurately tracks the last successfully *downloaded* message ID, preventing the loss of queued files on restart.
- **Automatic Cleanup of 0-Byte Files**: Automatically detects and deletes empty files created from failed downloads, keeping the download directory clean.

### Changed
- **Project Renamed to TeleGrab**: The project has been rebranded to better reflect its power and purpose.
- **Refactored Configuration**: Simplified and reorganized `config.json` to be more intuitive, with `free_settings` and `premium_settings` blocks for clear, hierarchical configuration.
- **Improved Download Logic**: The core download logic is now more resilient and efficient, focusing on stability for parallel operations.

### Removed
- **Dead Code and Obsolete Functions**: Removed several unused functions (`is_valid_file_size`, `is_valid_extension`, etc.) and their corresponding CLI arguments (`--ignore-size-limit`, etc.) to clean up the codebase.
- **Redundant Top-Level Settings**: Cleaned up `config.json` by removing settings that are now managed under `premium_settings` and `free_settings`.

## [1.0.0] - 2025-07-31

### Added
- Initial release of Telegram Media Downloader
- Support for downloading media from Telegram groups and channels
- Resume functionality to continue from where it left off
- Concurrent downloads with configurable limits
- Date-based file organization
- Progress tracking and detailed logging
- Rate limiting protection to avoid Telegram bans
- File type and size filtering
- Memory usage monitoring
- Automatic cleanup and state management
- Interactive setup mode with guided configuration
- Date filtering for specific time ranges
- Password-protected channel support
- CSV export for download statistics
- State encryption for security
- Multi-threading for better performance
- Extension filtering with open-ended list (jpg, png, txt, sql, csv, json, xml, and many more)
- Custom download directory support
- API credentials management
- GitHub Actions CI/CD setup
- Comprehensive documentation and guides

### Fixed
- **Rate Limiting Issues:** Fixed FloodWaitError by implementing proper rate limiting
- **Configuration Updates:** Updated default settings for free accounts to prevent bans
- **Memory Management:** Improved memory usage monitoring and cleanup
- **Error Handling:** Enhanced error handling for connection issues
- **State Management:** Fixed state file saving issues
- **Documentation:** Added comprehensive troubleshooting guides

### Changed
- **Default Settings:** Updated for safer free account usage
  - `max_concurrent`: 10 → 3
  - `delay_between_batches`: 2 → 5 seconds
  - `batch_size`: 100 → 20
  - `account_type`: "premium" → "free"
- **Rate Limiting:** Implemented conservative settings to avoid Telegram bans
- **Documentation:** Added troubleshooting section with common issues and solutions
- **Performance:** Optimized for stability over speed

### Security
- Added state file encryption support
- Secure API credentials management
- Automatic cleanup of temporary files
- Password support for protected channels

### Documentation
- Added comprehensive README with troubleshooting guide
- Created quick start guide with common issues
- Added rate limiting guidelines for different account types
- Included performance tips and best practices
- Added file organization examples
- Created contributing guidelines
- Added security policy
- Included issue and pull request templates

### Performance
- Implemented intelligent rate limiting
- Added memory usage monitoring
- Optimized batch processing
- Enhanced concurrent download management
- Added automatic cleanup features

### Configuration
- Added account type-specific settings
- Implemented dynamic configuration based on account type
- Added file size limit controls
- Enhanced extension filtering
- Added date range filtering
- Implemented custom directory support

### Monitoring
- Added detailed logging system
- Implemented progress tracking
- Added memory usage monitoring
- Created CSV export functionality
- Added download statistics

### User Experience
- Created interactive setup mode
- Added guided configuration process
- Implemented resume functionality
- Added progress indicators
- Created comprehensive error messages
- Added help documentation

### Development
- Set up GitHub Actions for CI/CD
- Added comprehensive testing
- Created development guidelines
- Implemented version control
- Added changelog tracking

### Dependencies
- Telethon >= 1.34.0
- Cryptg >= 0.4.0
- Cryptography >= 41.0.0
- Psutil >= 5.9.0

### Known Issues
- Rate limiting may occur with aggressive settings
- Large file downloads may be slow on free accounts
- Memory usage may be high with many concurrent downloads

### Future Plans
- Add support for more file types
- Implement advanced filtering options
- Add GUI interface
- Enhance performance monitoring
- Add cloud storage integration
- Implement advanced scheduling features

---

**Note:** This is the initial release with comprehensive features and documentation. The project is ready for production use with proper configuration. 
