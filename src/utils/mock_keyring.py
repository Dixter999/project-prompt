#!/usr/bin/env python3
"""
Mock implementation of keyring for testing purposes.
"""
import os
import json
from pathlib import Path

# Mock storage file
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.config/project-prompt")
MOCK_KEYRING_FILE = os.path.join(DEFAULT_CONFIG_DIR, "mock_keyring.json")

def _ensure_config_dir():
    """Ensure the config directory exists."""
    os.makedirs(os.path.dirname(MOCK_KEYRING_FILE), exist_ok=True)

def _load_keyring():
    """Load the keyring data from file."""
    _ensure_config_dir()
    try:
        if os.path.exists(MOCK_KEYRING_FILE):
            with open(MOCK_KEYRING_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_keyring(data):
    """Save the keyring data to file."""
    _ensure_config_dir()
    with open(MOCK_KEYRING_FILE, 'w') as f:
        json.dump(data, f)

def get_password(service_name, username):
    """Get a password from the keyring."""
    keyring = _load_keyring()
    return keyring.get(service_name, {}).get(username)

def set_password(service_name, username, password):
    """Set a password in the keyring."""
    keyring = _load_keyring()
    if service_name not in keyring:
        keyring[service_name] = {}
    keyring[service_name][username] = password
    _save_keyring(keyring)

def delete_password(service_name, username):
    """Delete a password from the keyring."""
    keyring = _load_keyring()
    if service_name in keyring and username in keyring[service_name]:
        del keyring[service_name][username]
        _save_keyring(keyring)
        return True
    return False
