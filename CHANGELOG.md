# Changelog

All notable changes to ProjectPrompt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-06-02

### Changed
- **Made all features available for all users**: Removed premium subscription requirements
- All AI-powered analysis, code generation, refactoring, and testing features are now freely accessible
- Eliminated subscription checks and premium feature restrictions

### Removed
- Premium subscription system and license validation
- Subscription manager and related premium-only feature gates
- Premium status checks across all commands

### Features Now Available to All Users
- AI-powered code analysis and error detection
- Advanced code refactoring capabilities
- Detailed code explanations with advanced analysis levels
- Premium dashboard with architecture analysis
- Automatic test generation
- Completeness verification tools
- Implementation assistant with detailed guides

## [1.0.0] - 2025-05-27

### Added
- **Core CLI Interface**: Complete command-line interface with `project-prompt` command
- **Project Analysis**: Comprehensive project structure and functionality analysis
- **AI Integration**: Support for Anthropic Claude and OpenAI APIs
- **Multi-Python Support**: Compatible with Python 3.8, 3.9, 3.10, and 3.11
- **Configuration Management**: Secure API key storage and configuration management
- **Interactive Features**: Menu system and dashboard functionality
- **Documentation Tools**: Built-in documentation navigation and generation
- **Premium Features**: Subscription management and license validation

### Technical Features
- Poetry-based dependency management
- Typer-based CLI framework
- Rich console interface for beautiful output
- Keyring integration for secure credential storage
- YAML-based configuration system
- Comprehensive error handling and logging

### Fixed
- ConfigManager attribute errors in telemetry system
- CI workflow complexity reduced for stable operation
- Dependencies properly declared in pyproject.toml
- Entry points correctly configured for CLI execution

### Infrastructure
- GitHub Actions CI for Python 3.8-3.11 compatibility testing
- Simplified CI workflow focusing on core functionality
- Proper package structure for pip installation

## [0.9.0] - 2023-09-15
- Beta release with core functionality
- Limited to internal testing

## [0.8.0] - 2023-08-01
- Alpha release with initial feature set
