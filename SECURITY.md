# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of ProjectPrompt seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly**
2. **Email us** at [security@example.com] with details about the vulnerability
3. You should receive a response within 48 hours
4. We will work with you to understand and address the issue
5. Once the vulnerability is fixed, we will credit you (unless you prefer to remain anonymous)

## Security Measures

ProjectPrompt implements several security measures:

1. Dependencies are regularly updated through Dependabot
2. All code changes undergo review through pull requests
3. We follow secure coding practices

## Third-party API Keys and Tokens

When using this project with Anthropic Claude or other APIs:

1. Never commit API keys to the repository
2. Use environment variables or .env files (added to .gitignore)
3. Review the permissions granted to any API keys
