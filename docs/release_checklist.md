# ProjectPrompt - Release Checklist

This document defines the checklist for preparing a ProjectPrompt release. Follow this guide to ensure that the release meets quality standards and is ready for users.

## Pre-Release Checklist

### Documentation

- [ ] All documentation is updated with new features
- [ ] Version number is updated in all relevant files (pyproject.toml)
- [ ] User guide reflects the current software behavior
- [ ] Installation instructions are verified
- [ ] README.md contains up-to-date information
- [ ] Changes are documented in the CHANGELOG.md file

### Code

- [ ] All PRs related to the release have been merged
- [ ] All conflicts are resolved
- [ ] Linting has been run on all source code
- [ ] Code reviews have been performed for important changes
- [ ] All unit and integration tests pass successfully
- [ ] Security scanning has been performed
- [ ] Dependencies have been updated to the latest versions
- [ ] Se ha verificado la compatibilidad con versiones anteriores
- [ ] Los TODOs críticos han sido resueltos o documentados

### Testing

- [ ] Se han ejecutado todas las pruebas unitarias
- [ ] The functionality has been verified on major operating systems:
  - [ ] Windows 10/11
  - [ ] macOS
  - [ ] Linux (Ubuntu/Debian)
- [ ] Manual tests of critical scenarios have been performed
- [ ] The freemium system has been verified
- [ ] Integration with Anthropic has been tested

### Packages and Distribution

- [ ] Version number has been incremented according to SemVer
- [ ] Distribution packages have been generated (sdist, wheel)
- [ ] Packages have been installed and verified in a clean environment
- [ ] Dependencies have been updated if necessary
- [ ] External dependencies have been minimized
- [ ] VS Code extension package (.vsix) has been tested

## Release Procedure

1. **Final Preparation**
   - Run `./verify_and_deploy.sh` for complete verification
   - Review the output and resolve any identified issues

2. **Version Generation**
   - Update the version in `pyproject.toml` and other relevant files
   - Create a commit with the message "Release vX.Y.Z"
   - Create a tag: `git tag -a vX.Y.Z -m "Version X.Y.Z"`

3. **Publication**
   - Push the tag to Github: `git push origin vX.Y.Z`
   - GitHub Actions will automatically:
     - Run tests on all platforms
     - Build Python packages, executables, and VS Code extension
     - Create a GitHub Release
     - Publish to PyPI
     - Publish to VS Code Marketplace
4. **Post-Release Verification**
   - Verify installation from PyPI: `pip install project-prompt`
   - Verify that online documentation is updated
   - Verify that main functionalities work correctly
   - Test the VS Code extension installation from the marketplace

5. **Announcement**
   - Publish announcement on official channels
   - Update the project website with the new version
   - Notify important users or collaborators
   - Post on relevant social media and developer forums

## Post-Release Tasks

- [ ] Begin planning for next version
- [ ] Review and categorize user feedback
- [ ] Open issues for any problems found
- [ ] Update the project roadmap
- [ ] Analyze adoption and installation metrics
- [ ] Monitor initial user reports and feedback

## Emergency Hotfix Procedure

In case a critical error is detected after publication:

1. Create a branch from the version tag: `git checkout -b hotfix-vX.Y.Z vX.Y.Z`
2. Implement the solution and corresponding tests
3. Update the version to vX.Y.(Z+1)
4. Follow the release procedure for the new version
5. Document the problem and solution in CHANGELOG.md
6. Notify users about the fix
