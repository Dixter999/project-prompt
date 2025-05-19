# ProjectPrompt Freemium System

## Overview

ProjectPrompt uses a freemium model where basic functionality is available for free while more advanced features require an API key. This document explains the freemium system implementation, how features are gated, and how to integrate with AI provider APIs.

## Feature Tiers

### Free Tier

The free tier provides basic functionality that doesn't require external API access:

| Feature | Description | Implementation |
|---------|-------------|---------------|
| Project Analysis | Basic project structure analysis | `quick_analyze.py` |
| Project Initialization | Create new project structures | `quick_init.py` |
| Basic Prompt Generation | Simple contextual prompts | `src/generators/prompt_generator.py` |

### Premium Tier

The premium tier requires API authentication and provides advanced capabilities:

| Feature | Description | Implementation | API Dependency |
|---------|-------------|---------------|---------------|
| Enhanced Prompts | Advanced contextual prompts | `src/generators/contextual_prompt_generator.py` | Anthropic |
| Implementation Prompts | Detailed implementation guidance | `src/generators/implementation_prompt_generator.py` | Anthropic |
| Documentation Generation | Auto-generated project docs | `src/generators/markdown_generator.py` | Anthropic (Optional) |
| Connectivity Analysis | Module dependency analysis | `src/analyzers/connectivity_analyzer.py` | None |

## Implementation Details

The freemium system is implemented through several components:

### 1. API Key Management

API keys are stored securely in the configuration system:

```python
# src/utils/config_manager.py
def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider."""
    config = get_config()
    return config.get("api_keys", {}).get(provider)

def set_api_key(provider: str, key: str) -> bool:
    """Set API key for a specific provider."""
    config = get_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][provider] = key
    return save_config(config)
```

### 2. Feature Verification

Before executing premium features, the system checks for appropriate API keys:

```python
# src/utils/license_validator.py
def verify_feature_access(feature: str) -> bool:
    """Verify access to a premium feature."""
    if feature in FREE_FEATURES:
        return True
    
    if feature in ANTHROPIC_FEATURES:
        return bool(config_manager.get_api_key("anthropic"))
    
    if feature in GITHUB_FEATURES:
        return bool(config_manager.get_api_key("github"))
    
    return False
```

### 3. Feature Lists

The system maintains lists of which features belong to which tier:

```python
# src/utils/license_validator.py
FREE_FEATURES = [
    "analyze",
    "init",
    "basic-prompts",
]

ANTHROPIC_FEATURES = [
    "enhanced-prompts",
    "implementation-prompts",
    "docs",
]

GITHUB_FEATURES = [
    "connectivity",
]
```

## API Integration

### Anthropic API

The system integrates with Anthropic Claude for advanced NLP tasks:

```python
# src/integrations/anthropic.py
def generate_completion(prompt: str, max_tokens: int = 500) -> str:
    """Generate a completion using Anthropic API."""
    api_key = config_manager.get_api_key("anthropic")
    
    if not api_key:
        raise ValueError("Anthropic API key not found. Premium feature unavailable.")
    
    # API request implementation
    # ...
```

### GitHub API

For repository analysis and code fetching:

```python
# src/integrations/github.py
def fetch_repository_info(repo_url: str) -> Dict[str, Any]:
    """Fetch information about a GitHub repository."""
    api_key = config_manager.get_api_key("github")
    
    if not api_key:
        raise ValueError("GitHub API key not found. Premium feature unavailable.")
    
    # API request implementation
    # ...
```

## Freemium System Verification

A verification tool is provided to ensure the system correctly restricts premium features:

```bash
# Run the verification tool
python verify_freemium_system.py
```

The tool tests:

- Which features are correctly gated
- Whether API keys unlock appropriate features
- Edge cases like expired or invalid keys

## User Experience

### Feature Discoverability

The CLI provides feedback when premium features are requested but unavailable:

```
$ project-prompt generate-prompts --enhanced
Error: Enhanced prompts require an Anthropic API key.
To set your API key, run: project-prompt set-api anthropic YOUR_API_KEY
```

### Setting API Keys

Users can set API keys through the CLI:

```bash
project-prompt set-api anthropic YOUR_API_KEY
```

Or by editing the config file directly.

## Adding New Premium Features

To add a new premium feature:

1. Add the feature name to the appropriate list in `src/utils/license_validator.py`
2. Implement proper API key verification in the feature implementation
3. Add clear error messages when API keys are missing
4. Update the verification tool to test the new feature

Example:

```python
def my_premium_feature():
    if not verify_feature_access("my-feature"):
        raise ValueError(
            "This premium feature requires a valid API key. "
            "Please run 'project-prompt set-api provider YOUR_API_KEY'"
        )
    
    # Feature implementation
    # ...
```

## Testing the Freemium System

Test the freemium system with:

```bash
# Run the test script
./run_freemium_tests.sh

# Or run individual tests
python test_freemium_system.py
```
