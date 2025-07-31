# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | Yes |
| < 1.0   | No  |

## Reporting a Vulnerability

If you discover a security vulnerability in Telegram Media Downloader, please report it privately via GitHub issues (mark as security) or open a private discussion. Do not post vulnerabilities publicly until a fix is released.

## Security Best Practices

### For Users

1. Keep credentials secure
   - Never share your API credentials
   - Use environment variables when possible
   - Regularly rotate your API keys

2. Session file security
   - Keep session files in a secure location
   - Don't commit session files to version control
   - Use .gitignore to exclude sensitive files

3. Network security
   - Use VPN when downloading from public networks
   - Be cautious with public WiFi
   - Monitor your download activity

4. File validation
   - Scan downloaded files with antivirus software
   - Verify file integrity when possible
   - Be cautious with executable files

### For Developers

1. Code security
   - Follow secure coding practices
   - Validate all user inputs
   - Use parameterized queries
   - Implement proper error handling

2. Dependency management
   - Keep dependencies updated
   - Monitor for known vulnerabilities
   - Use pip audit to check for issues

3. API security
   - Implement rate limiting
   - Validate API responses
   - Handle authentication errors gracefully

## Known Security Considerations

### Telegram API Limitations

1. Rate limiting
   - Telegram has built-in rate limits
   - Our script includes delays to respect these limits
   - Excessive requests may result in temporary bans

2. Session management
   - Session files contain authentication data
   - Keep them secure and private
   - Don't share session files between users

3. Privacy considerations
   - Downloaded content may contain personal information
   - Respect privacy and copyright laws
   - Don't redistribute content without permission

### File System Security

1. Download directory
   - Ensure proper permissions on download directory
   - Don't download to system directories
   - Use dedicated directories for downloads

2. File permissions
   - Set appropriate file permissions
   - Don't make downloaded files executable by default
   - Use secure file naming conventions

## Security Updates

Security updates will be announced in the repository releases and changelog.

## Security Checklist

- Code security review completed
- Dependencies updated and audited
- Security tests passing
- No hardcoded credentials
- Proper error handling implemented
- Input validation in place
- Rate limiting configured
- Logging configured (no sensitive data)

## Contact

For any security concerns, please use GitHub issues (mark as security) or private discussions.

## Acknowledgments

We thank security researchers and contributors who help improve the security of this project. Responsible disclosure is appreciated and will be acknowledged in our security advisories.

---

Note: This security policy is a living document and will be updated as needed. Please check back regularly for the latest information. 