#!/bin/bash
cd /mnt/h/Projects/project-prompt
git checkout main
git merge --no-ff fix/github-actions-v4 -m "Merge fix/github-actions-v4 into main: Updated GitHub Actions from v3 to v4 and fixed VS Code extension gitignore"
git push origin main
