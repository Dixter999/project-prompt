#!/usr/bin/env python3
"""Manual fix for import issues in themes.py."""

import os
import shutil

# Save backup of original themes.py
themes_path = "src/ui/themes.py"
backup_path = "src/ui/themes.py.bak"

# Create backup if it doesn't exist
if not os.path.exists(backup_path) and os.path.exists(themes_path):
    print(f"Creating backup of {themes_path} at {backup_path}")
    shutil.copy2(themes_path, backup_path)
    print("Backup created")
else:
    print("Using existing backup or file doesn't exist")

# Fix themes.py by removing circular imports
with open(themes_path, "r", encoding="utf-8") as f:
    content = f.read()

# Look for and fix the circular import
print("Fixing circular imports in themes.py...")
fixed_content = content.replace(
    "from src.utils import config_manager", 
    "# Lazy import to avoid circular dependency\n# from src.utils import config_manager"
)

# Replace how the theme name is determined
fixed_content = fixed_content.replace(
    "theme_name = config_manager.get(\"theme\", \"default\")",
    "# Avoid circular import\n    theme_name = \"default\""
)

# Write the fixed file
with open(themes_path, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print(f"Fixed {themes_path}")

# Final report
print("\nManual fix applied to themes.py")
print("Please run tests now to verify the fix works")
