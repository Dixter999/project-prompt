#!/usr/bin/env python3
"""Quick git status check and resolution"""

import subprocess
import sys
import os

os.chdir('/mnt/h/Projects/project-prompt')

def run_git_cmd(cmd):
    """Run git command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env={**os.environ, 'PAGER': 'cat'})
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    print("=== Git Status Check ===")
    
    # Check current branch
    stdout, stderr, code = run_git_cmd('git branch --show-current')
    print(f"Current branch: {stdout}")
    
    # Check if working directory is clean
    stdout, stderr, code = run_git_cmd('git status --porcelain')
    if stdout:
        print(f"Working directory status:\n{stdout}")
    else:
        print("Working directory: CLEAN")
    
    # Check current commit
    stdout, stderr, code = run_git_cmd('git rev-parse HEAD')
    print(f"Current commit: {stdout}")
    
    # Check if we're ahead/behind remote
    stdout, stderr, code = run_git_cmd('git status --porcelain=v1 --branch')
    if stdout:
        branch_line = stdout.split('\n')[0]
        print(f"Branch tracking: {branch_line}")
    
    # Try to push
    print("\n=== Attempting Push ===")
    stdout, stderr, code = run_git_cmd('git push origin main')
    if code == 0:
        print("✅ Push successful!")
        return True
    else:
        print(f"❌ Push failed: {stderr}")
        
        # Try force push
        print("\n=== Attempting Force Push ===")
        stdout, stderr, code = run_git_cmd('git push origin main --force')
        if code == 0:
            print("✅ Force push successful!")
            return True
        else:
            print(f"❌ Force push failed: {stderr}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
