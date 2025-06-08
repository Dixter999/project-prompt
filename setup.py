"""
Setup configuration for ProjectPrompt v2.0
"""

import os
import sys
import platform
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

# Read README for long description
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "ProjectPrompt - AI-powered project analysis and suggestions tool"

# Read version from __init__.py
def get_version():
    try:
        with open('src/__init__.py', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "2.0.0"

# Core dependencies
DEPENDENCIES = [
    "anthropic>=0.7.0",
    "openai>=1.0.0", 
    "click>=8.0.0",
    "python-dotenv>=0.19.0",
    "pathspec>=0.10.0",
    "typing-extensions>=4.0.0"
]

class PostInstallCommand(_install):
    """Custom install command to ensure CLI accessibility."""
    
    def run(self):
        _install.run(self)
        self.setup_cli_access()
    
    def setup_cli_access(self):
        """Setup CLI command accessibility."""
        try:
            self.create_shell_aliases()
            self.verify_installation()
            self.print_success_message()
        except Exception as e:
            print(f"⚠️  CLI setup warning: {e}")
            print("📖 See README.md for manual setup instructions")
    
    def create_shell_aliases(self):
        """Create shell aliases for common shells."""
        home = Path.home()
        
        # Shell configurations to update
        shell_configs = {
            '.bashrc': 'bash',
            '.zshrc': 'zsh',
            '.profile': 'profile'
        }
        
        alias_line = 'alias projectprompt="python -m src.cli"'
        
        for config_file, shell_name in shell_configs.items():
            config_path = home / config_file
            
            try:
                if config_path.exists():
                    # Read existing content
                    content = config_path.read_text(encoding='utf-8')
                    
                    # Skip if alias already exists
                    if 'alias projectprompt=' in content:
                        continue
                    
                    # Add alias to the end
                    with open(config_path, 'a', encoding='utf-8') as f:
                        f.write(f'\n# ProjectPrompt CLI alias (auto-added)\n{alias_line}\n')
                    
                    print(f"✅ Added alias to {config_file}")
                    
            except (PermissionError, OSError) as e:
                print(f"⚠️  Could not update {config_file}: {e}")
    
    def verify_installation(self):
        """Verify the installation works."""
        try:
            import src.cli
            print("✅ ProjectPrompt CLI module imported successfully")
        except ImportError as e:
            print(f"⚠️  CLI import issue: {e}")
    
    def print_success_message(self):
        """Print installation success message."""
        print("\n" + "="*60)
        print("🎉 ProjectPrompt installation completed!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("1️⃣  Restart your terminal (or run: source ~/.bashrc)")
        print("2️⃣  Test with: projectprompt --help")
        print("3️⃣  If command not found, use: python -m src.cli --help")
        print("4️⃣  See README.md for setup and usage examples")
        print("\n🔧 If you have issues:")
        print("   • Check PATH: echo $PATH")
        print("   • Manual alias: alias projectprompt='python -m src.cli'")
        print("   • Full path: python -m src.cli --help")
        print("="*60)

setup(
    name="projectprompt",
    version=get_version(),
    description="AI-powered project analysis and improvement suggestions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="ProjectPrompt",
    url="https://github.com/your-username/projectprompt",
    packages=find_packages(include=["src", "src.*", "."]),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "projectprompt=src.cli:main",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai, code-analysis, project-analysis",
    include_package_data=True,
    zip_safe=False,
)
