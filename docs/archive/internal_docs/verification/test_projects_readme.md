# Anthropic Verification Tools

This directory contains specialized tools for testing and verifying the markdown generation capabilities of Anthropic's Claude API in ProjectPrompt.

## Contents

- Verification scripts for testing Anthropic markdown generation
- Project templates for different application types
- Test projects automatically generated during verification
- Output markdown files from Anthropic analysis
- Quality metrics and test logs

## Available Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `check_anthropic_env.py` | Verify environment setup | `python check_anthropic_env.py` |
| `quick_test_anthropic.py` | Run a quick sanity check | `python quick_test_anthropic.py` |
| `enhanced_verify_anthropic.py` | Run detailed quality checks | `python enhanced_verify_anthropic.py --project-types web-project backend-api` |
| `create_test_project.py` | Create test projects | `python create_test_project.py --type web-project --name "My Test Project"` |
| `advanced_markdown_metrics.py` | Analyze markdown quality | `python advanced_markdown_metrics.py <markdown_file>` |
| `test_verification_system.py` | Run unit tests for verification | `python test_verification_system.py` |
| `test_with_anthropic_api.sh` | Test with live API calls | `./test_with_anthropic_api.sh` |
| `run_all_verifications.sh` | Run basic verification suite | `./run_all_verifications.sh` |
| `run_comprehensive_tests.sh` | Run complete verification | `./run_comprehensive_tests.sh` |

## Project Templates

The `/templates` directory contains project templates for testing with different types of applications:

- `web-project`: Frontend web application
- `backend-api`: RESTful API with FastAPI
- `mobile-app`: React Native mobile application
- `data-science`: Data science project with analysis notebooks
- `cli-tool`: Command-line interface tool
- `library`: Reusable library package
- `game-dev`: Game development project with ECS architecture
- `mixed`: Multi-component project combining multiple templates

## Usage

### Quick Verification

```bash
# Verify environment setup
python check_anthropic_env.py

# Run a quick test
python quick_test_anthropic.py
```

### Comprehensive Verification

```bash
# Run all verification methods
./run_comprehensive_tests.sh

# Run with specific project types
./run_comprehensive_tests.sh --types web-project backend-api
```

## File Naming Conventions

- `anthropic_test_project_*` - Automatically generated test projects
- `anthropic_analysis_*.md` - Output markdown files from Anthropic analysis
- `verification_results_*.json` - Quality metrics from verification tests
- `test_results_*.log` - Logs from test execution
- `.env.test` - Temporary environment file used during testing

## Documentation

For more detailed information, see:
- `/mnt/h/Projects/project-prompt/docs/anthropic_verification_guide.md`
