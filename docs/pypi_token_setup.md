# PyPI Token Setup Guide

This document provides instructions for setting up a PyPI API token for secure package publishing.

## Why Use API Tokens?

PyPI has deprecated username/password authentication in favor of token-based authentication. API tokens provide:

1. Enhanced security (no password sharing)
2. Limited scope (can be scoped to specific projects)
3. Ability to revoke access without changing your password
4. Usage in CI/CD pipelines without exposing your account credentials

## Creating a PyPI API Token

1. Sign in to your account on [PyPI](https://pypi.org/)
2. Navigate to your account settings
3. Select "API tokens" from the menu
4. Click "Add API token"
5. Provide a token name (e.g., "ProjectPrompt-CI")
6. Choose the appropriate scope:
   - "All projects" (if you want to upload any package)
   - "Specific project" (if you only want to authorize uploads for a single project)
7. Click "Create token"
8. **Important**: Copy your token immediately - it will only be shown once!

## Setting Up Token For Local Development

### Method 1: Using .pypirc file

Create or edit the `.pypirc` file in your home directory:

```
[pypi]
username = __token__
password = pypi-AgEIcH...your-token-here...
```

### Method 2: Using Environment Variables

Set the following environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcH...your-token-here...
```

### Method 3: Using the Upload Script

We've created a convenient script for uploading to PyPI:

```bash
./upload_to_pypi.sh "pypi-YOUR-TOKEN-HERE"
```

This script will build the package, check it with twine, and upload it to PyPI using your token.

## Setting Up Token in GitHub Actions

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI token
6. Click "Add secret"

The GitHub workflow is already configured to use this secret for PyPI publishing.

## Testing Your Token

To test if your token is working correctly:

```bash
pip install twine
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

This will upload to TestPyPI instead of the main PyPI repository, allowing you to test your setup.

## Troubleshooting

If you encounter upload errors:

1. Verify your token is correct and not expired
2. Make sure you're using `__token__` as the username 
3. Check that the token has the correct scope for your project
4. Ensure your package version is unique (PyPI doesn't allow overwriting existing versions)