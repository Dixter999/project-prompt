# Rule Models Test Report

Generated: 2025-06-01 18:14:49

## Summary

- **Total Tests:** 12
- **Passed:** 10
- **Failed:** 2
- **Success Rate:** 83.3%

## Test Results

| Test | Status | Message |
|------|--------|---------|
| import_rule_models | ✅ | All rule model classes imported successfully |
| enum_classes | ✅ | Verified 3 priorities and 9 categories |
| rule_context | ✅ | RuleContext creation and configuration works |
| rule_item | ✅ | RuleItem creation and methods work correctly |
| rule_group | ✅ | RuleGroup creation and methods work correctly |
| rule_set | ✅ | RuleSet creation and methods work correctly |
| rule_template | ✅ | RuleTemplate creation and generation work correctly |
| predefined_templates | ✅ | All predefined templates work correctly |
| yaml_export | ❌ | YAML export test failed |
| rule_conflicts | ✅ | Conflict detection works (found 4 issues) |
| file_matching | ✅ | All 5 file matching scenarios work correctly |
| integration | ❌ | Integration test failed |

## Failed Tests Details

### yaml_export
- **Message:** YAML export test failed
- **Details:** 'RuleSet' object has no attribute 'to_yaml'

### integration
- **Message:** Integration test failed
- **Details:** name 'RulePriority' is not defined


## Recommendations

⚠️ **2 tests failed.** Review the failed tests and:

1. Check that all dependencies are installed
2. Verify the rule_models.py file is complete
3. Ensure all imports are working correctly
4. Check for any syntax or logic errors
