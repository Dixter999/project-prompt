#!/usr/bin/env python3
"""Simple script to test imports with tracing."""

import sys

# Print where we are
print(f"Starting import tests with trace")

# Try a single import
print("Importing src...")
import src
print(f"Imported src, version: {src.__version__}")

# Exit immediately
print("Done testing imports")
sys.exit(0)
