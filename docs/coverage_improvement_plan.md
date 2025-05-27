# Coverage Improvement Plan

## Option 1: Add Tests for More Modules (Recommended)
Create tests for these high-value modules:

1. **api_validator.py** (currently 25% coverage)
   - Add tests for API key validation
   - Mock external API calls
   - Test error handling

2. **markdown_manager.py** (currently 11% coverage) 
   - Test markdown generation
   - Test template processing
   - Test file operations

3. **project_structure.py** (currently 14% coverage)
   - Test directory scanning
   - Test structure analysis
   - Test output formatting

## Option 2: Exclude Untested Modules
Update .coveragerc to exclude modules without tests:

```ini
[run]
source = src/utils
omit = 
    */tests/*
    src/utils/adaptive_system.py
    src/utils/check_api_key.py
    src/utils/check_premium_status.py
    src/utils/fix_config_in_telemetry.py
    src/utils/generate_developer_credentials.py
    src/utils/quick_analyze.py
    src/utils/quick_init.py
    src/utils/restructure_project.py
    src/utils/send_analysis_to_anthropic.py
    src/utils/set_anthropic_key.py
    src/utils/simple_analyze.py
    src/utils/structure_improvement.py
    src/utils/sync_manager.py
    src/utils/telemetry.py
    src/utils/updater.py
```

## Option 3: Gradual Coverage Increase
Start with current focus, then gradually add module coverage:

Week 1: Focus on config.py + logger.py (current)
Week 2: Add api_validator.py tests
Week 3: Add project_structure.py tests
Week 4: Add markdown_manager.py tests
