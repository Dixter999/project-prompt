#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mock keyring implementation for CI environment.

This module replaces the real keyring with a memory-based implementation
that works in CI environments without a real backend.
"""

import sys
import types

# Create a mock keyring module to avoid backend issues
mock_keyring = types.ModuleType('keyring')

# Add mock functions
class MemoryKeyring:
    def __init__(self):
        self.store = {}
        
    def get_password(self, service_name, username):
        key = f"{service_name}:{username}"
        return self.store.get(key)
        
    def set_password(self, service_name, username, password):
        key = f"{service_name}:{username}"
        self.store[key] = password
        
    def delete_password(self, service_name, username):
        key = f"{service_name}:{username}"
        if key in self.store:
            del self.store[key]
            return True
        return False

_keyring = MemoryKeyring()
mock_keyring.get_password = _keyring.get_password
mock_keyring.set_password = _keyring.set_password
mock_keyring.delete_password = _keyring.delete_password

# Replace the real keyring with our mock
sys.modules['keyring'] = mock_keyring
print("✅ Keyring module patched for CI tests")
