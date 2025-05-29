#!/usr/bin/env python3
"""
Simple test for enhanced free dashboard
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
from src.utils.config import ConfigManager

# Quick test
config = ConfigManager()
config.set_premium(False)  # Set to free tier

dashboard_gen = MarkdownDashboardGenerator("/mnt/h/Projects/project-prompt", config)

# Test the new method
try:
    basic_features = dashboard_gen._generate_free_features_section()
    print("✅ Free features section generated successfully!")
    print(f"Length: {len(basic_features)} characters")
    print("Preview:")
    print(basic_features[:500] + "..." if len(basic_features) > 500 else basic_features)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
