# ProjectPrompt Installation Guide

## 🚨 "Command not found: project-prompt"

**Quick Fix (works for 90% of users):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 📋 Solutions

### 1. **Check Installation**
```bash
pip list | grep projectprompt
# If not installed: pip install projectprompt
```

### 2. **Fix PATH (Most Common)**
```bash
# For zsh (macOS/Linux default):
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3. **Alternative: Use Python Module**
```bash
python -m src.main version
python -m src.main help
python -m src.main menu
```

### 4. **Reinstall with --user**
```bash
pip install --user projectprompt
```

### 5. **For Python 3.12+ Users**
If you get `No module named pkg_resources`:
```bash
pip install setuptools
pip install --force-reinstall projectprompt
```

## 🚀 Quick Start

Once working:
```bash
# Verify
project-prompt version

# Quick setup
project-prompt menu

# Manual setup
project-prompt set-api anthropic
cd /your/project
project-prompt init
project-prompt analyze
```

## 🔧 Advanced Solutions

### Virtual Environments
```bash
source venv/bin/activate
pip install projectprompt
```

### Multiple Python Versions
```bash
python3 -m pip install projectprompt
python3 -m src.main version
```

### Windows
```cmd
setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python3X\Scripts"
```

### Create Alias
```bash
echo 'alias pp="project-prompt"' >> ~/.zshrc
source ~/.zshrc
```

---

**Need help?** Run `project-prompt help` or `project-prompt menu` for interactive setup.
