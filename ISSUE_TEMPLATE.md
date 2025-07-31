# Issue Template

## Before Submitting

- [ ] I have searched the existing issues to avoid duplicates
- [ ] I have checked the documentation for solutions
- [ ] I have tested with the latest version from main branch
- [ ] I have provided all necessary information

## Issue Type

Please select the type of issue:

- [ ] **Bug Report** - Something isn't working as expected
- [ ] **Feature Request** - Suggest an idea for this project
- [ ] **Documentation** - Report an issue with the documentation
- [ ] **Question** - Ask a question about the project
- [ ] **Other** - Something else

## Environment Information

**Operating System:**
- [ ] Windows
- [ ] macOS
- [ ] Linux (specify distribution: ___________)
- [ ] Other (specify: ___________)

**Python Version:**
```
python --version
```

**Telegram Media Downloader Version:**
```
python telegram_media_downloader.py --version
```

## Description

### For Bug Reports

**What happened?**
A clear and concise description of what the bug is.

**What did you expect to happen?**
A clear and concise description of what you expected to happen.

**Steps to reproduce:**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Error messages:**
```
Paste any error messages here
```

**Log files:**
```
Paste relevant log entries here
```

### For Feature Requests

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like:**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered:**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context:**
Add any other context or screenshots about the feature request here.

## Configuration

**config.json (remove sensitive information):**
```json
{
  "api_id": "YOUR_API_ID",
  "api_hash": "YOUR_API_HASH",
  "download_dir": "downloads",
  "max_file_size_mb": 100,
  "media_types": ["photo", "video", "document"]
}
```

**Command used:**
```bash
python telegram_media_downloader.py --target "YOUR_TARGET"
```

## Additional Information

**Screenshots:**
If applicable, add screenshots to help explain your problem.

**Additional context:**
Add any other context about the problem here.

## Checklist

- [ ] I have provided all required information
- [ ] I have tested with different configurations
- [ ] I have checked the logs for errors
- [ ] I have tried the troubleshooting steps in README.md
- [ ] I have searched for similar issues

---

**Note**: Please be respectful and constructive in your issue report. We appreciate your help in improving this project! 