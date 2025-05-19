# Pending Task: Fix Unit Tests for Contextual Prompt Generator

After implementing Task 3.3 "Generación de prompts contextuales mejorados", we have identified some issues with the unit tests due to circular imports in the project structure.

## Issues Identified

1. Circular imports between modules:
   - `src.generators.markdown_generator` and `src.utils.documentation_system`
   - `src.analyzers.project_scanner` and other analyzer modules

2. Test failures in `test_contextual_prompt_generator.py` due to:
   - Incorrect patching of dependencies
   - Interface mismatches with the actual implementation
   - Circular imports making testing difficult

## Tasks to Complete

1. Refactor the project to resolve circular imports:
   - Move factory functions (`get_*`) to separate modules
   - Use dependency injection patterns where applicable
   - Consider extracting interfaces to break dependencies

2. Fix unit tests for `ContextualPromptGenerator`:
   - Update patch targets to match actual implementation
   - Fix constructor arguments in test code
   - Consider using integration tests instead of unit tests for components with complex dependencies

## Proposed Timeline

- Priority: Medium
- Estimated time: 1-2 days
- Suggested branch: `fix/contextual-prompt-generator-tests`

## References

- Committed implementation: feature/enhanced-prompts (commit 99147b1)
- Related issue: Task 3.3 in Phase 3
