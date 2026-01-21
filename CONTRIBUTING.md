# Contributing to Android Automation Skill

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🐛 Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Device model and Android version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs or screenshots

## 💡 Suggesting Features

1. Open an issue with the "feature request" label
2. Describe the use case
3. Provide examples if possible

## 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/android-automation-skill.git
cd android-automation-skill

# Make scripts executable
chmod +x scripts/**/*.sh scripts/**/*.py

# Connect a device or start an emulator
adb devices
```

## 📝 Code Style

- Use Python 3.8+ features
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints where possible
- All scripts should support `--format json` and `--format text`

## ✅ Testing Your Changes

```bash
# Test with a connected device
./scripts/device/list_devices.sh
python3 scripts/device/device_info.py
python3 scripts/interaction/screenshot.py --output test.png
```

## 📤 Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m "Add: new feature description"`
6. Push to your fork: `git push origin feature/my-feature`
7. Open a Pull Request

## 📋 Pull Request Checklist

- [ ] Code follows project style
- [ ] All scripts have `--help` support
- [ ] JSON output is properly formatted
- [ ] Tested on real device or emulator
- [ ] Documentation updated if needed

## 🏷️ Commit Message Format

```
Type: Short description

Longer description if needed.

Types:
- Add: New feature
- Fix: Bug fix
- Update: Enhancement to existing feature
- Remove: Removed feature
- Docs: Documentation only
```

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
