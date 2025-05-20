#!/usr/bin/env python3
"""
Test template for classes in {{module_path}}.
"""
import pytest
from {{module_path}} import {{class_name}}

class Test{{class_name}}:
    """Tests for the {{class_name}} class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {{class_name}}()
        
    def teardown_method(self):
        """Tear down test fixtures."""
        pass
    
    {{test_cases}}
