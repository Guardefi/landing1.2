# Test Commands Reference

This folder contains all the test commands and scripts used during the codebase fixes. Each file contains commands you can run to validate different aspects of the system.

## Quick Reference

1. **`pre-commit-commands.ps1`** - Pre-commit hook commands
2. **`lint-commands.ps1`** - Linting and code quality checks
3. **`test-commands.ps1`** - Core application tests
4. **`docker-commands.ps1`** - Docker and containerization tests
5. **`backend-specific-tests.ps1`** - Backend-specific validation
6. **`frontend-tests.ps1`** - Frontend validation commands
7. **`database-tests.ps1`** - Database and migration tests
8. **`security-tests.ps1`** - Security and vulnerability checks
9. **`performance-tests.ps1`** - Performance and load testing
10. **`troubleshooting-commands.ps1`** - Debugging and diagnostic commands
11. **`file-cleanup-commands.ps1`** - File cleanup and organization utilities

## Usage

Each PowerShell script can be run individually:

```powershell
# Run all pre-commit checks
.\test-commands\pre-commit-commands.ps1

# Run specific tests
.\test-commands\test-commands.ps1

# Check linting status
.\test-commands\lint-commands.ps1
```

## File Organization

- **Commands**: Each `.ps1` file contains executable PowerShell commands
- **Expected Output**: Comments show what successful output should look like
- **Error Handling**: Commands include error checking and troubleshooting tips
- **Dependencies**: Prerequisites are listed at the top of each file
