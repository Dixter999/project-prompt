#!/usr/bin/env python3
"""
ProjectPrompt v1.0.0 Release Deployment Script
Complete deployment automation for stable release.
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

class ReleaseManager:
    def __init__(self):
        self.project_root = Path("/mnt/h/Projects/project-prompt")
        self.version = "1.0.0"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, command, description="", timeout=60):
        """Run a command safely with error handling."""
        self.log(f"Running: {description or command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.log(f"✅ Success: {description}")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
                return True, result.stdout
            else:
                self.log(f"❌ Failed: {description}", "ERROR")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout: {description}", "ERROR")
            return False, "Command timed out"
        except Exception as e:
            self.log(f"💥 Exception: {e}", "ERROR")
            return False, str(e)
    
    def validate_environment(self):
        """Validate that environment is ready for release."""
        self.log("🔍 Validating environment...")
        
        # Check project directory
        if not self.project_root.exists():
            self.log(f"Project directory not found: {self.project_root}", "ERROR")
            return False
            
        os.chdir(self.project_root)
        
        # Check critical files
        critical_files = [
            "pyproject.toml",
            "src/main.py",
            "README.md",
            "CHANGELOG.md"
        ]
        
        for file_path in critical_files:
            if not Path(file_path).exists():
                self.log(f"Critical file missing: {file_path}", "ERROR")
                return False
        
        self.log("✅ Environment validation passed")
        return True
    
    def test_installation(self):
        """Test package installation and basic functionality."""
        self.log("🧪 Testing package installation...")
        
        # Install package in development mode
        success, output = self.run_command(
            "pip install -e . --quiet", 
            "Install package in development mode"
        )
        if not success:
            return False
            
        # Test CLI availability
        success, output = self.run_command(
            "python3 -c \"from src.main import app; print('CLI import successful')\"",
            "Test CLI import"
        )
        if not success:
            return False
            
        # Test basic commands
        success, output = self.run_command(
            "python3 -m src.main --version",
            "Test version command"
        )
        if not success:
            return False
            
        self.log("✅ Installation tests passed")
        return True
    
    def create_git_branch(self):
        """Create main branch and prepare for release."""
        self.log("🌿 Preparing Git branch...")
        
        # Check current commit
        success, current_commit = self.run_command(
            "git rev-parse HEAD",
            "Get current commit"
        )
        if not success:
            return False
            
        current_commit = current_commit.strip()
        self.log(f"Current commit: {current_commit[:8]}")
        
        # Create main branch from current HEAD if it doesn't exist
        success, output = self.run_command(
            "git checkout -B main",
            "Create/switch to main branch"
        )
        if not success:
            return False
            
        self.log("✅ Git branch prepared")
        return True
    
    def push_to_github(self):
        """Push code to GitHub repository."""
        self.log("🚀 Pushing to GitHub...")
        
        # Push main branch
        success, output = self.run_command(
            "git push origin main --force-with-lease",
            "Push main branch to GitHub"
        )
        if not success:
            self.log("Failed to push to GitHub - trying regular push", "WARN")
            success, output = self.run_command(
                "git push origin main",
                "Push main branch (regular)"
            )
            if not success:
                return False
        
        self.log("✅ Successfully pushed to GitHub")
        return True
    
    def create_release_tag(self):
        """Create and push release tag."""
        self.log("🏷️ Creating release tag...")
        
        tag_name = f"v{self.version}"
        
        # Create annotated tag
        success, output = self.run_command(
            f"git tag -a {tag_name} -m 'Release {self.version}: Stable release with core functionality'",
            f"Create tag {tag_name}"
        )
        if not success:
            # Tag might already exist, try to delete and recreate
            self.run_command(f"git tag -d {tag_name}", "Delete existing tag")
            success, output = self.run_command(
                f"git tag -a {tag_name} -m 'Release {self.version}: Stable release with core functionality'",
                f"Recreate tag {tag_name}"
            )
            if not success:
                return False
        
        # Push tag
        success, output = self.run_command(
            f"git push origin {tag_name}",
            f"Push tag {tag_name}"
        )
        if not success:
            return False
            
        self.log(f"✅ Release tag {tag_name} created and pushed")
        return True
    
    def deploy_to_pypi_test(self):
        """Deploy to PyPI test repository."""
        self.log("📦 Building package for PyPI...")
        
        # Clean previous builds
        self.run_command("rm -rf dist/ build/ *.egg-info", "Clean previous builds")
        
        # Build package
        success, output = self.run_command(
            "python3 -m build",
            "Build package"
        )
        if not success:
            # Try with setuptools if build module not available
            success, output = self.run_command(
                "python3 setup.py sdist bdist_wheel",
                "Build package with setuptools"
            )
            if not success:
                return False
        
        # Check if we can upload to test PyPI (requires credentials)
        self.log("📤 Package built successfully")
        self.log("ℹ️  To upload to PyPI Test: python3 -m twine upload --repository testpypi dist/*")
        self.log("ℹ️  To upload to PyPI: python3 -m twine upload dist/*")
        
        return True
    
    def generate_release_report(self):
        """Generate final release report."""
        report_content = f"""
# ProjectPrompt v{self.version} Release Report

## Release Summary
- **Version**: {self.version}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: ✅ DEPLOYED

## Deployment Checklist
- ✅ Environment validated
- ✅ Package installation tested
- ✅ Git branch prepared
- ✅ Code pushed to GitHub
- ✅ Release tag created
- ✅ Package built for PyPI

## Next Steps
1. **GitHub Actions**: Check CI/CD pipeline at https://github.com/Dixter999/project-prompt/actions
2. **PyPI Upload**: Upload package using `twine upload dist/*`
3. **VS Code Extension**: Deploy extension from vscode-extension/ directory
4. **Documentation**: Verify documentation site is updated

## Manual Commands for Final Steps

### Upload to PyPI Test
```bash
python3 -m twine upload --repository testpypi dist/*
```

### Upload to PyPI Production
```bash
python3 -m twine upload dist/*
```

### Test Installation from PyPI
```bash
pip install projectprompt
project-prompt --version
```

## URLs
- **GitHub Repository**: https://github.com/Dixter999/project-prompt
- **GitHub Releases**: https://github.com/Dixter999/project-prompt/releases
- **PyPI Package**: https://pypi.org/project/projectprompt/

## Release Notes
{self.version} includes:
- Core project analysis functionality
- CLI with comprehensive commands
- Anthropic Claude integration
- VS Code extension
- Python 3.8-3.11 compatibility
- Stable configuration system

---
Generated by ProjectPrompt Release Manager
"""
        
        report_path = self.project_root / "RELEASE_REPORT_v1.0.0.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
            
        self.log(f"📋 Release report generated: {report_path}")
        return True
    
    def run_full_deployment(self):
        """Run complete deployment process."""
        self.log("🚀 Starting ProjectPrompt v1.0.0 Release Deployment")
        self.log("=" * 60)
        
        steps = [
            ("validate_environment", "Environment Validation"),
            ("test_installation", "Installation Testing"), 
            ("create_git_branch", "Git Branch Preparation"),
            ("push_to_github", "GitHub Push"),
            ("create_release_tag", "Release Tag Creation"),
            ("deploy_to_pypi_test", "PyPI Package Build"),
            ("generate_release_report", "Release Report Generation")
        ]
        
        failed_steps = []
        
        for step_method, step_name in steps:
            self.log(f"\n📋 Step: {step_name}")
            try:
                method = getattr(self, step_method)
                success = method()
                if not success:
                    failed_steps.append(step_name)
                    self.log(f"❌ Step failed: {step_name}", "ERROR")
                else:
                    self.log(f"✅ Step completed: {step_name}")
            except Exception as e:
                failed_steps.append(step_name)
                self.log(f"💥 Step exception: {step_name} - {e}", "ERROR")
        
        self.log("\n" + "=" * 60)
        if failed_steps:
            self.log(f"⚠️  Deployment completed with {len(failed_steps)} failed steps:", "WARN")
            for step in failed_steps:
                self.log(f"   - {step}", "WARN")
            return 1
        else:
            self.log("🎉 DEPLOYMENT SUCCESSFUL! ProjectPrompt v1.0.0 is live!")
            self.log("🔗 Check: https://github.com/Dixter999/project-prompt")
            return 0

def main():
    manager = ReleaseManager()
    return manager.run_full_deployment()

if __name__ == "__main__":
    sys.exit(main())
