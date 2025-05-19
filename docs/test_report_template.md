# ProjectPrompt Test Report Template

## Test Environment

- **Date**: [DATE]
- **Tester**: [NAME]
- **OS**: [OPERATING SYSTEM]
- **Python Version**: [VERSION]
- **ProjectPrompt Version**: [VERSION]

## Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| Basic Analysis | PASS/FAIL | |
| Project Structure Analysis | PASS/FAIL | |
| Project Initialization | PASS/FAIL | |
| Functionality Comparison | PASS/FAIL | |
| Standalone Analyzer | PASS/FAIL | |
| Project Subparts Analysis | PASS/FAIL | |
| Output Format Testing | PASS/FAIL | |
| Documentation Generation | PASS/FAIL/SKIPPED | |
| Connectivity Analysis | PASS/FAIL/SKIPPED | |
| Freemium System | PASS/FAIL/SKIPPED | |

**Overall Result**: [PASS/FAIL]

## Detailed Test Results

### 1. Basic Analysis

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py analyze /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected output**:
- Project structure identified
- Python detected as main language
- Correct file count

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 2. Project Structure Analysis

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api /mnt/h/Projects/project-prompt/test_results/structure_analysis.json
```

**Expected output**:
- JSON file created
- Contains language breakdown
- Contains file statistics

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 3. Project Initialization

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py init test-project --path /mnt/h/Projects/project-prompt/test_results
```

**Expected output**:
- Project directory created
- Standard structure (src, tests, docs)
- Basic files (README, setup.py)

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 4. Functionality Comparison

**Method**:
- Compare source and generated project structures

**Expected output**:
- Similar structure but with differences
- Core components present in both

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 5. Standalone Analyzer

**Command executed**:
```bash
cd /mnt/h/Projects/project-prompt && python quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected output**:
- Analysis runs successfully
- Similar output to integrated command

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 6. Project Subparts Analysis

**Command executed**:
```bash
cd /mnt/h/Projects/project-prompt && python quick_analyze.py /mnt/h/Projects/project-prompt/test-projects/weather-api/src
```

**Expected output**:
- Analysis of src directory only
- Fewer files than full project analysis

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 7. Output Format Testing

**Command executed**:
```bash
cd /mnt/h/Projects/project-prompt && python project_analyzer.py /mnt/h/Projects/project-prompt/test-projects/weather-api /mnt/h/Projects/project-prompt/test_results/full_analysis.json
```

**Expected output**:
- Detailed JSON output
- More comprehensive than quick analyzer

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 8. Documentation Generation

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py docs /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected output**:
- Generated documentation in markdown
- Key modules and classes documented

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL/SKIPPED]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 9. Connectivity Analysis

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/project_prompt.py connections /mnt/h/Projects/project-prompt/test-projects/weather-api
```

**Expected output**:
- Module dependency graph
- Identified imports between files

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL/SKIPPED]
**Comments**: [ADDITIONAL OBSERVATIONS]

### 10. Freemium System Testing

**Command executed**:
```bash
python /mnt/h/Projects/project-prompt/verify_freemium_system.py
```

**Expected output**:
- Validation of free vs premium features
- Proper access control based on API key

**Actual output**:
- [NOTES ABOUT OUTPUT]

**Status**: [PASS/FAIL/SKIPPED]
**Comments**: [ADDITIONAL OBSERVATIONS]

## Issues Discovered

1. [ISSUE 1 DESCRIPTION]
   - Severity: High/Medium/Low
   - Impact: [DESCRIBE IMPACT]
   - Reproduction Steps: [HOW TO REPRODUCE]

2. [ISSUE 2 DESCRIPTION]
   - Severity: High/Medium/Low
   - Impact: [DESCRIBE IMPACT]
   - Reproduction Steps: [HOW TO REPRODUCE]

## Recommendations

1. [RECOMMENDATION 1]
2. [RECOMMENDATION 2]
3. [RECOMMENDATION 3]

## Attachments

- [LIST ANY TEST OUTPUT FILES OR SCREENSHOTS]
