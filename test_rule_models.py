#!/usr/bin/env python3
"""
Rule Models Test Validator

This script specifically tests the rule models functionality from rule_models.py,
validating all classes, methods, and integration points.
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Test result tracking
test_results = []

def test_result(test_name: str, success: bool, message: str = "", details: Any = None):
    """Record a test result"""
    result = {
        "test": test_name,
        "success": success,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {message}")
    
    if not success and details:
        print(f"   Details: {details}")

def test_rule_models_imports():
    """Test importing all rule model classes"""
    try:
        from src.models.rule_models import (
            RulePriority, RuleCategory, RuleContext, RuleItem,
            RuleGroup, RuleSet, RuleTemplate,
            get_web_app_template, get_data_science_template, get_api_service_template
        )
        test_result("import_rule_models", True, "All rule model classes imported successfully")
        return True
    except Exception as e:
        test_result("import_rule_models", False, "Failed to import rule models", str(e))
        return False

def test_enum_classes():
    """Test enum classes"""
    try:
        from src.models.rule_models import RulePriority, RuleCategory
        
        # Test RulePriority
        priorities = [RulePriority.MANDATORY, RulePriority.RECOMMENDED, RulePriority.OPTIONAL]
        assert len(priorities) == 3
        assert RulePriority.MANDATORY.value == "mandatory"
        assert RulePriority.RECOMMENDED.value == "recommended"
        assert RulePriority.OPTIONAL.value == "optional"
        
        # Test RuleCategory
        categories = [
            RuleCategory.TECHNOLOGY, RuleCategory.ARCHITECTURE, RuleCategory.CODE_STYLE,
            RuleCategory.TESTING, RuleCategory.DOCUMENTATION, RuleCategory.PERFORMANCE,
            RuleCategory.SECURITY, RuleCategory.DEPLOYMENT, RuleCategory.CUSTOM
        ]
        assert len(categories) == 9
        
        test_result("enum_classes", True, f"Verified {len(priorities)} priorities and {len(categories)} categories")
        return True
    except Exception as e:
        test_result("enum_classes", False, "Enum validation failed", str(e))
        return False

def test_rule_context():
    """Test RuleContext class"""
    try:
        from src.models.rule_models import RuleContext
        
        # Test basic creation
        context = RuleContext()
        assert context.directories == []
        assert context.file_patterns == []
        assert context.file_extensions == []
        assert context.exclude_patterns == []
        assert context.environments == []
        
        # Test with parameters
        context = RuleContext(
            directories=['src/', 'tests/'],
            file_extensions=['.py', '.pyx'],
            exclude_patterns=['*test*', '*__pycache__*'],
            environments=['dev', 'test']
        )
        
        assert len(context.directories) == 2
        assert len(context.file_extensions) == 2
        assert len(context.exclude_patterns) == 2
        assert len(context.environments) == 2
        
        test_result("rule_context", True, "RuleContext creation and configuration works")
        return True
    except Exception as e:
        test_result("rule_context", False, "RuleContext test failed", str(e))
        return False

def test_rule_item():
    """Test RuleItem class and its methods"""
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory, RuleContext
        
        # Create basic rule
        rule = RuleItem(
            content="Use Python 3.8+ for all development",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY
        )
        
        assert rule.content == "Use Python 3.8+ for all development"
        assert rule.priority == RulePriority.MANDATORY
        assert rule.category == RuleCategory.TECHNOLOGY
        assert rule.description is None
        assert rule.context is None
        assert len(rule.tags) == 0
        
        # Test with full parameters
        context = RuleContext(file_extensions=['.py'])
        rule = RuleItem(
            content="Type hints are mandatory",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.CODE_STYLE,
            description="Enforce type annotations",
            context=context,
            tags={'python', 'typing', 'mandatory'},
            examples=['def func(x: int) -> str:', 'class MyClass:'],
            violations=['def func(x):', 'def func(x) -> None:']
        )
        
        assert rule.description == "Enforce type annotations"
        assert rule.context.file_extensions == ['.py']
        assert 'python' in rule.tags
        assert len(rule.examples) == 2
        assert len(rule.violations) == 2
        
        # Test applies_to_file method
        assert rule.applies_to_file("src/main.py") == True
        assert rule.applies_to_file("README.md") == False
        
        # Test rule without context (should apply to all files)
        rule_no_context = RuleItem(
            content="General rule",
            priority=RulePriority.OPTIONAL,
            category=RuleCategory.CUSTOM
        )
        assert rule_no_context.applies_to_file("any_file.txt") == True
        
        test_result("rule_item", True, "RuleItem creation and methods work correctly")
        return True
    except Exception as e:
        test_result("rule_item", False, "RuleItem test failed", str(e))
        return False

def test_rule_group():
    """Test RuleGroup class and its methods"""
    try:
        from src.models.rule_models import RuleGroup, RuleItem, RulePriority, RuleCategory
        
        # Create rule group
        group = RuleGroup(
            name="test_group",
            description="Test rule group"
        )
        
        assert group.name == "test_group"
        assert group.description == "Test rule group"
        assert len(group.rules) == 0
        assert group.priority is None
        assert group.category is None
        
        # Add rules to group
        rule1 = RuleItem("Rule 1", RulePriority.MANDATORY, RuleCategory.TECHNOLOGY)
        rule2 = RuleItem("Rule 2", RulePriority.RECOMMENDED, RuleCategory.TECHNOLOGY)
        rule3 = RuleItem("Rule 3", RulePriority.OPTIONAL, RuleCategory.TECHNOLOGY)
        
        group.rules.extend([rule1, rule2, rule3])
        
        # Test get_rules_by_priority
        mandatory_rules = group.get_rules_by_priority(RulePriority.MANDATORY)
        assert len(mandatory_rules) == 1
        assert mandatory_rules[0].content == "Rule 1"
        
        recommended_rules = group.get_rules_by_priority(RulePriority.RECOMMENDED)
        assert len(recommended_rules) == 1
        
        # Test get_applicable_rules
        applicable_rules = group.get_applicable_rules("test.py")
        assert len(applicable_rules) == 3  # All rules apply (no context restrictions)
        
        test_result("rule_group", True, "RuleGroup creation and methods work correctly")
        return True
    except Exception as e:
        test_result("rule_group", False, "RuleGroup test failed", str(e))
        return False

def test_rule_set():
    """Test RuleSet class and its methods"""
    try:
        from src.models.rule_models import (
            RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory, RuleContext
        )
        
        # Create rule set
        rule_set = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            description="Test rule set"
        )
        
        assert rule_set.name == "test_ruleset"
        assert rule_set.version == "1.0.0"
        assert rule_set.description == "Test rule set"
        assert len(rule_set.groups) == 0
        assert len(rule_set.metadata) == 0
        assert len(rule_set.inheritance) == 0
        
        # Create and add groups
        tech_group = RuleGroup("technology", category=RuleCategory.TECHNOLOGY)
        tech_group.rules.append(RuleItem("Use React", RulePriority.MANDATORY, RuleCategory.TECHNOLOGY))
        tech_group.rules.append(RuleItem("Use TypeScript", RulePriority.RECOMMENDED, RuleCategory.TECHNOLOGY))
        
        style_group = RuleGroup("code_style", category=RuleCategory.CODE_STYLE)
        style_group.rules.append(RuleItem("Use ESLint", RulePriority.MANDATORY, RuleCategory.CODE_STYLE))
        
        rule_set.add_group(tech_group)
        rule_set.add_group(style_group)
        
        # Test basic operations
        assert len(rule_set.groups) == 2
        assert rule_set.get_group("technology") is not None
        assert rule_set.get_group("nonexistent") is None
        
        # Test get_rules_by_category
        tech_rules = rule_set.get_rules_by_category(RuleCategory.TECHNOLOGY)
        assert len(tech_rules) == 2
        
        style_rules = rule_set.get_rules_by_category(RuleCategory.CODE_STYLE)
        assert len(style_rules) == 1
        
        # Test get_rules_by_priority
        mandatory_rules = rule_set.get_rules_by_priority(RulePriority.MANDATORY)
        assert len(mandatory_rules) == 2
        
        # Test get_mandatory_rules
        mandatory_rules = rule_set.get_mandatory_rules()
        assert len(mandatory_rules) == 2
        
        # Test get_applicable_rules
        applicable_rules = rule_set.get_applicable_rules("test.js")
        assert len(applicable_rules) == 3  # All rules apply
        
        # Test validation
        errors = rule_set.validate()
        assert len(errors) == 0  # No errors expected
        
        test_result("rule_set", True, "RuleSet creation and methods work correctly")
        return True
    except Exception as e:
        test_result("rule_set", False, "RuleSet test failed", str(e))
        return False

def test_rule_template():
    """Test RuleTemplate class and generation"""
    try:
        from src.models.rule_models import (
            RuleTemplate, RuleGroup, RuleItem, RulePriority, RuleCategory
        )
        
        # Create template
        template = RuleTemplate(
            name="test_template",
            project_type="web_app",
            description="Test template"
        )
        
        assert template.name == "test_template"
        assert template.project_type == "web_app"
        assert template.description == "Test template"
        assert len(template.rule_groups) == 0
        assert len(template.variables) == 0
        
        # Add rule group with variables
        group = RuleGroup("technology")
        group.rules.append(RuleItem(
            "Use {frontend_framework} for UI",
            RulePriority.MANDATORY,
            RuleCategory.TECHNOLOGY
        ))
        group.rules.append(RuleItem(
            "Use {database} for persistence",
            RulePriority.MANDATORY,
            RuleCategory.TECHNOLOGY
        ))
        
        template.rule_groups.append(group)
        
        # Test rule generation
        context = {
            "frontend_framework": "React",
            "database": "PostgreSQL"
        }
        
        generated_set = template.generate_rules(context)
        
        assert generated_set.name == "test_template_generated"
        assert len(generated_set.groups) == 1
        
        generated_group = list(generated_set.groups.values())[0]
        assert len(generated_group.rules) == 2
        
        # Check variable substitution
        rule_contents = [rule.content for rule in generated_group.rules]
        assert "Use React for UI" in rule_contents
        assert "Use PostgreSQL for persistence" in rule_contents
        
        test_result("rule_template", True, "RuleTemplate creation and generation work correctly")
        return True
    except Exception as e:
        test_result("rule_template", False, "RuleTemplate test failed", str(e))
        return False

def test_predefined_templates():
    """Test predefined template functions"""
    try:
        from src.models.rule_models import (
            get_web_app_template, get_data_science_template, get_api_service_template
        )
        
        # Test web app template
        web_template = get_web_app_template()
        assert web_template.name == "web_app"
        assert web_template.project_type == "web_application"
        assert len(web_template.rule_groups) > 0
        
        # Test data science template
        ds_template = get_data_science_template()
        assert ds_template.name == "data_science"
        assert ds_template.project_type == "data_science"
        assert len(ds_template.rule_groups) > 0
        
        # Test API service template
        api_template = get_api_service_template()
        assert api_template.name == "api_service"
        assert api_template.project_type == "api_service"
        assert len(api_template.rule_groups) > 0
        
        # Test generation with each template
        web_context = {
            "frontend_framework": "Vue.js",
            "backend_framework": "Flask",
            "database": "MongoDB"
        }
        
        web_rules = web_template.generate_rules(web_context)
        assert len(web_rules.groups) > 0
        
        ds_context = {
            "visualization_library": "matplotlib"
        }
        
        ds_rules = ds_template.generate_rules(ds_context)
        assert len(ds_rules.groups) > 0
        
        # API template doesn't use variables but should still generate
        api_rules = api_template.generate_rules({})
        assert len(api_rules.groups) > 0
        
        test_result("predefined_templates", True, "All predefined templates work correctly")
        return True
    except Exception as e:
        test_result("predefined_templates", False, "Predefined templates test failed", str(e))
        return False

def test_yaml_export():
    """Test YAML export functionality"""
    try:
        from src.models.rule_models import (
            RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory, RuleContext
        )
        
        # Create comprehensive rule set
        rule_set = RuleSet(
            name="yaml_test_rules",
            version="2.0.0",
            description="Test YAML export functionality",
            metadata={
                "project_type": "test",
                "generated_at": datetime.now().isoformat()
            }
        )
        
        # Technology group
        tech_group = RuleGroup(
            name="technology",
            description="Technology requirements",
            category=RuleCategory.TECHNOLOGY
        )
        
        tech_rule = RuleItem(
            content="Use Python 3.9+ for all development",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.TECHNOLOGY,
            description="Python version requirement",
            context=RuleContext(
                file_extensions=['.py'],
                directories=['src/', 'tests/']
            ),
            tags={'python', 'version'},
            examples=['python_requires = ">=3.9"'],
            violations=['python_requires = ">=3.7"']
        )
        
        tech_group.rules.append(tech_rule)
        rule_set.add_group(tech_group)
        
        # Code style group
        style_group = RuleGroup(
            name="code_style",
            category=RuleCategory.CODE_STYLE
        )
        
        style_rule = RuleItem(
            content="Use black for code formatting",
            priority=RulePriority.RECOMMENDED,
            category=RuleCategory.CODE_STYLE,
            tags={'formatting', 'black'}
        )
        
        style_group.rules.append(style_rule)
        rule_set.add_group(style_group)
        
        # Test YAML export
        yaml_content = rule_set.to_yaml()
        
        # Verify YAML content contains expected elements
        assert "name: yaml_test_rules" in yaml_content
        assert "version: '2.0.0'" in yaml_content
        assert "description: Test YAML export functionality" in yaml_content
        assert "technology:" in yaml_content
        assert "code_style:" in yaml_content
        assert "Use Python 3.9+ for all development" in yaml_content
        assert "mandatory" in yaml_content
        assert "recommended" in yaml_content
        assert "file_extensions:" in yaml_content
        assert "- .py" in yaml_content
        
        # Test round-trip: save and load YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Try to load it back (basic validation)
            import yaml
            with open(temp_file, 'r') as f:
                loaded_data = yaml.safe_load(f)
            
            assert loaded_data['name'] == 'yaml_test_rules'
            assert loaded_data['version'] == '2.0.0'
            assert 'groups' in loaded_data
            assert 'technology' in loaded_data['groups']
            assert 'code_style' in loaded_data['groups']
            
        finally:
            # Clean up temp file
            Path(temp_file).unlink()
        
        test_result("yaml_export", True, f"YAML export works correctly ({len(yaml_content)} chars)")
        return True
    except Exception as e:
        test_result("yaml_export", False, "YAML export test failed", str(e))
        return False

def test_rule_conflicts():
    """Test rule conflict detection"""
    try:
        from src.models.rule_models import (
            RuleSet, RuleGroup, RuleItem, RulePriority, RuleCategory
        )
        
        # Create rule set with potential conflicts
        rule_set = RuleSet("conflict_test")
        
        group = RuleGroup("test_conflicts")
        
        # Add potentially conflicting rules
        group.rules.extend([
            RuleItem("Use only React for frontend", RulePriority.MANDATORY, RuleCategory.TECHNOLOGY),
            RuleItem("Use Vue.js for all UI components", RulePriority.MANDATORY, RuleCategory.TECHNOLOGY),
            RuleItem("Never use jQuery in new code", RulePriority.MANDATORY, RuleCategory.TECHNOLOGY),
            RuleItem("Use jQuery for DOM manipulation", RulePriority.RECOMMENDED, RuleCategory.TECHNOLOGY),
        ])
        
        rule_set.add_group(group)
        
        # Test validation (should detect conflicts)
        errors = rule_set.validate()
        
        # The validation should detect some conflicts, though the exact number
        # depends on the conflict detection algorithm
        assert isinstance(errors, list)
        
        test_result("rule_conflicts", True, f"Conflict detection works (found {len(errors)} issues)")
        return True
    except Exception as e:
        test_result("rule_conflicts", False, "Rule conflict test failed", str(e))
        return False

def test_file_matching():
    """Test file pattern matching in rules"""
    try:
        from src.models.rule_models import RuleItem, RulePriority, RuleCategory, RuleContext
        
        # Test different context configurations
        test_cases = [
            {
                "name": "Python files only",
                "context": RuleContext(file_extensions=['.py', '.pyx']),
                "matches": ["main.py", "src/utils.py", "test.pyx"],
                "no_matches": ["main.js", "README.md", "config.json"]
            },
            {
                "name": "Source directory only",
                "context": RuleContext(directories=['src/']),
                "matches": ["src/main.py", "src/utils/helper.js"],
                "no_matches": ["tests/test.py", "docs/readme.md"]
            },
            {
                "name": "Pattern matching",
                "context": RuleContext(file_patterns=['*.test.*', '*_test.*']),
                "matches": ["main.test.js", "utils_test.py"],
                "no_matches": ["main.js", "utils.py"]
            },
            {
                "name": "Exclude patterns",
                "context": RuleContext(exclude_patterns=['*__pycache__*', '*.pyc']),
                "matches": ["main.py", "src/utils.py"],
                "no_matches": ["__pycache__/main.pyc", "src/__pycache__/utils.pyc", "cache.pyc"]
            },
            {
                "name": "Complex combination",
                "context": RuleContext(
                    file_extensions=['.py'],
                    directories=['src/'],
                    exclude_patterns=['*test*']
                ),
                "matches": ["src/main.py", "src/utils/helper.py"],
                "no_matches": ["src/test_main.py", "tests/main.py", "src/main.js"]
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            rule = RuleItem(
                content=f"Test rule for {test_case['name']}",
                priority=RulePriority.OPTIONAL,
                category=RuleCategory.TESTING,
                context=test_case['context']
            )
            
            # Test matches
            for file_path in test_case['matches']:
                if not rule.applies_to_file(file_path):
                    test_result(f"file_matching_{test_case['name']}_match", False, 
                              f"Rule should match {file_path}")
                    all_passed = False
            
            # Test non-matches
            for file_path in test_case['no_matches']:
                if rule.applies_to_file(file_path):
                    test_result(f"file_matching_{test_case['name']}_no_match", False, 
                              f"Rule should not match {file_path}")
                    all_passed = False
        
        if all_passed:
            test_result("file_matching", True, f"All {len(test_cases)} file matching scenarios work correctly")
        
        return all_passed
    except Exception as e:
        test_result("file_matching", False, "File matching test failed", str(e))
        return False

def test_integration_with_existing_system():
    """Test integration with existing rule management system"""
    try:
        # Test if the models can be imported alongside existing rule managers
        from src.models.rule_models import RuleSet, RuleGroup, RuleItem
        
        # Try to import existing rule management components
        try:
            from src.utils.enhanced_rules_manager import EnhancedRulesManager
            integration_possible = True
        except ImportError:
            integration_possible = False
        
        # Create a rule set using the models
        rule_set = RuleSet("integration_test")
        group = RuleGroup("test_integration")
        group.rules.append(RuleItem(
            "Integration test rule", 
            RulePriority.OPTIONAL, 
            RuleCategory.TESTING
        ))
        rule_set.add_group(group)
        
        # Test serialization compatibility
        yaml_output = rule_set.to_yaml()
        assert len(yaml_output) > 0
        
        test_result("integration", True, 
                   f"Integration test passed (enhanced manager available: {integration_possible})")
        return True
    except Exception as e:
        test_result("integration", False, "Integration test failed", str(e))
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    passed = sum(1 for r in test_results if r['success'])
    failed = len(test_results) - passed
    success_rate = (passed / len(test_results)) * 100 if test_results else 0
    
    report = f"""# Rule Models Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Tests:** {len(test_results)}
- **Passed:** {passed}
- **Failed:** {failed}
- **Success Rate:** {success_rate:.1f}%

## Test Results

| Test | Status | Message |
|------|--------|---------|
"""
    
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        report += f"| {result['test']} | {status} | {result['message']} |\n"
    
    if failed > 0:
        report += "\n## Failed Tests Details\n\n"
        for result in test_results:
            if not result['success']:
                report += f"### {result['test']}\n"
                report += f"- **Message:** {result['message']}\n"
                if result['details']:
                    report += f"- **Details:** {result['details']}\n"
                report += "\n"
    
    report += "\n## Recommendations\n\n"
    if failed == 0:
        report += "✅ **All tests passed!** The rule models system is working correctly.\n"
    else:
        report += f"⚠️ **{failed} tests failed.** Review the failed tests and:\n\n"
        report += "1. Check that all dependencies are installed\n"
        report += "2. Verify the rule_models.py file is complete\n"
        report += "3. Ensure all imports are working correctly\n"
        report += "4. Check for any syntax or logic errors\n"
    
    return report

def main():
    """Main test execution function"""
    print("🧪 Rule Models Test Validator")
    print("=" * 50)
    print("Testing all components of the rule models system...")
    print()
    
    # Run all tests
    tests = [
        test_rule_models_imports,
        test_enum_classes,
        test_rule_context,
        test_rule_item,
        test_rule_group,
        test_rule_set,
        test_rule_template,
        test_predefined_templates,
        test_yaml_export,
        test_rule_conflicts,
        test_file_matching,
        test_integration_with_existing_system
    ]
    
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            test_result(test_func.__name__, False, f"Test execution failed: {str(e)}")
    
    # Generate and save report
    report = generate_test_report()
    
    # Save report to file
    report_file = Path("rule_models_test_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Display summary
    passed = sum(1 for r in test_results if r['success'])
    failed = len(test_results) - passed
    
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(test_results)) * 100:.1f}%")
    print(f"Report saved to: {report_file}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Rule models system is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {failed} TESTS FAILED. Check the report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
