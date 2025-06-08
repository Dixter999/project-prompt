# Installation Test Guide

## Testing the Enhanced Installation

### Test 1: Fresh Installation
```bash
# Clone the repository
git clone https://github.com/Dixter999/project-prompt.git
cd project-prompt

# Test enhanced installation
pip install -e .

# Should see automatic setup messages including:
# ✅ Added alias to .zshrc
# ✅ ProjectPrompt CLI module imported successfully
# 🎉 ProjectPrompt installation completed!
```

### Test 2: Installation Script
```bash
# Run the installation script
chmod +x install.sh
./install.sh

# Should see verification steps and success confirmation
```

### Test 3: CLI Access Verification
```bash
# Test direct command (should work after restart/source)
projectprompt --help

# Test fallback method (always works)
python -m src.cli --help

# Test alias creation
grep "projectprompt" ~/.zshrc
```

### Test 4: Troubleshooting Path
```bash
# If command not found, should work with full path
python -m src.cli --help

# Manual alias addition should work
echo 'alias projectprompt="python -m src.cli"' >> ~/.zshrc
source ~/.zshrc
projectprompt --help
```

## Expected Behavior

✅ **Success Indicators:**
- Installation shows automatic alias creation messages
- CLI command works: `projectprompt --help`
- Fallback works: `python -m src.cli --help`
- Aliases added to shell config files

⚠️ **Common Issues Handled:**
- PATH not updated → Manual alias instructions provided
- Shell config not writable → Fallback to python -m
- Permission issues → Clear error messages with solutions

## Installation Flow Summary

1. **Enhanced setup.py** automatically creates shell aliases
2. **install.sh script** provides comprehensive verification
3. **README.md** includes multiple installation methods and troubleshooting
4. **Fallback options** ensure CLI is always accessible via `python -m src.cli`
