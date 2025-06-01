# ProjectPrompt Test Report

**Generated:** 2025-06-01 18:14:45
**Duration:** 7.05 seconds
**Results Directory:** test-results-20250601-181436

## Summary

- **Total Tests:** 46
- **Passed:** 3
- **Failed:** 2
- **Errors:** 0
- **Skipped:** 0
- **Success Rate:** 60.0%

## Results by Category

### Basic

- Total: 5
- Passed: 3
- Failed: 2
- Errors: 0
- Success Rate: 60.0%

### Configuration

- Total: 7
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Analysis

- Total: 9
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Setup

- Total: 3
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Ai

- Total: 4
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Premium

- Total: 1
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Rules

- Total: 4
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Progress

- Total: 2
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Documentation

- Total: 2
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Utilities

- Total: 4
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Error_Handling

- Total: 3
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

### Api

- Total: 2
- Passed: 0
- Failed: 0
- Errors: 0
- Success Rate: 0.0%

## Detailed Test Results

| Test | Category | Result | Duration | Description |
|------|----------|--------|----------|-------------|
| version | basic | ✅ passed | 2.74s | Show version information |
| help_general | basic | ✅ passed | 0.85s | Show general help |
| help_analyze | basic | ❌ failed | 1.03s | Show analyze command help |
| help_config | basic | ❌ failed | 1.26s | Show config command help |
| diagnose | basic | ✅ passed | 1.13s | Run diagnostic checks |
| config_show | configuration | ❓ unknown | 0.00s | Show current configuration |
| config_list | configuration | ❓ unknown | 0.00s | List configuration options |
| check_env | configuration | ❓ unknown | 0.00s | Check environment variables |
| set_log_level_info | configuration | ❓ unknown | 0.00s | Set log level to INFO |
| set_log_level_debug | configuration | ❓ unknown | 0.00s | Set log level to DEBUG |
| config_set_name | configuration | ❓ unknown | 0.00s | Set project name |
| config_set_desc | configuration | ❓ unknown | 0.00s | Set project description |
| analyze | analysis | ❓ unknown | 0.00s | Analyze current project |
| analyze_detailed | analysis | ❓ unknown | 0.00s | Detailed project analysis |
| analyze_output | analysis | ❓ unknown | 0.00s | Analysis with output file |
| deps | analysis | ❓ unknown | 0.00s | Dependency analysis |
| deps_limited | analysis | ❓ unknown | 0.00s | Limited dependency analysis |
| deps_output | analysis | ❓ unknown | 0.00s | Dependency analysis with output |
| dashboard | analysis | ❓ unknown | 0.00s | Generate dashboard |
| dashboard_md | analysis | ❓ unknown | 0.00s | Dashboard in markdown format |
| dashboard_json | analysis | ❓ unknown | 0.00s | Dashboard in JSON format |
| init_folder | setup | ❓ unknown | 0.00s | Initialize project folder |
| setup_deps | setup | ❓ unknown | 0.00s | Setup dependencies |
| setup_alias | setup | ❓ unknown | 0.00s | Setup command alias |
| analyze_group_list | ai | ❓ unknown | 0.00s | List available groups |
| analyze_group_specific | ai | ❓ unknown | 0.00s | Analyze specific group |
| generate_suggestions | ai | ❓ unknown | 0.00s | Generate suggestions |
| ai_chat | ai | ❓ unknown | 0.00s | AI chat test |
| premium_list | premium | ❓ unknown | 0.00s | List premium features |
| rules_suggest | rules | ❓ unknown | 0.00s | Generate rule suggestions |
| rules_patterns | rules | ❓ unknown | 0.00s | Analyze project patterns |
| rules_project | rules | ❓ unknown | 0.00s | Generate project rules |
| rules_structured | rules | ❓ unknown | 0.00s | Generate structured rules |
| status | progress | ❓ unknown | 0.00s | Show sync status |
| track_progress | progress | ❓ unknown | 0.00s | Track progress |
| docs_list | documentation | ❓ unknown | 0.00s | List documentation |
| docs_search | documentation | ❓ unknown | 0.00s | Search documentation |
| telemetry_status | utilities | ❓ unknown | 0.00s | Check telemetry status |
| telemetry_disable | utilities | ❓ unknown | 0.00s | Disable telemetry |
| telemetry_enable | utilities | ❓ unknown | 0.00s | Enable telemetry |
| update_check | utilities | ❓ unknown | 0.00s | Check for updates |
| analyze_invalid_path | error_handling | ❓ unknown | 0.00s | Analysis with invalid path |
| group_nonexistent | error_handling | ❓ unknown | 0.00s | Analyze nonexistent group |
| config_invalid | error_handling | ❓ unknown | 0.00s | Set invalid config |
| verify_api | api | ❓ unknown | 0.00s | Verify API configuration |
| set_dummy_api | api | ❓ unknown | 0.00s | Set dummy Anthropic key |

## Recommendations

⚠️ **2 tests failed.** Consider the following:

1. Check API key configuration for AI features
2. Ensure all dependencies are installed (`pip install -r requirements.txt`)
3. Verify file permissions and access rights
4. Review error logs in individual test result files
5. Check network connectivity for API-dependent features