# Release Checklist

This checklist ensures all aspects of the project are ready for release.

## Pre-Release Checklist

### Code Quality ✅
- [x] All tests passing (321 tests)
- [x] Code coverage ≥70% (currently 74%)
- [x] All linting checks pass (ruff)
- [x] Type checking passes (mypy)
- [x] No security vulnerabilities in dependencies
- [x] Code follows project style guidelines

### Documentation ✅
- [x] README.md is complete and accurate
- [x] API documentation is complete
- [x] CLI documentation is complete
- [x] Getting started guide exists
- [x] Examples are provided
- [x] Contributing guide exists
- [x] All docstrings are present and accurate

### Package Configuration
- [ ] `pyproject.toml` metadata is complete
  - [ ] Version number is correct
  - [ ] Author information is correct
  - [ ] Description is accurate
  - [ ] Keywords are appropriate
  - [ ] Classifiers are correct
  - [ ] URLs point to correct locations
- [ ] Dependencies are properly specified
  - [ ] Runtime dependencies are correct
  - [ ] Version constraints are appropriate
  - [ ] Optional dependencies are properly categorized
- [ ] Entry points are configured correctly
- [ ] Package can be built successfully

### Testing
- [x] Unit tests pass (321 tests)
- [x] All critical modules have test coverage
- [ ] Package installs correctly in clean environment
- [ ] CLI command works after installation
- [ ] Import statements work correctly

### Error Handling
- [x] Error messages are user-friendly
- [x] Exceptions are properly typed
- [x] Error context is preserved
- [x] CLI error messages are helpful

### Performance
- [x] Async operations are properly implemented
- [x] Connection pooling is used
- [x] Token caching is implemented
- [x] Pagination is memory-efficient

### Security
- [x] Credentials are never logged
- [x] Sensitive data is masked in output
- [x] HTTPS is enforced
- [x] Input validation is present
- [x] Dependencies are up-to-date

### CLI
- [x] All commands work correctly
- [x] Help text is complete
- [x] Error messages are clear
- [x] Output formats work (table, JSON, CSV)
- [x] Configuration management works

## Release Process

### Version 0.1.0 (Initial Release)

1. **Final Code Review**
   - [ ] Review all recent changes
   - [ ] Check for any TODO comments
   - [ ] Verify no debug code remains
   - [ ] Ensure all features are documented

2. **Update Version**
   - [ ] Update version in `pyproject.toml`
   - [ ] Update version in `src/pysophoscentralapi/__version__.py`
   - [ ] Update version in `change-log.md`

3. **Update Documentation**
   - [ ] Update README with release notes
   - [ ] Update change-log.md with final entries
   - [ ] Verify all documentation links work
   - [ ] Update project-plan.md status

4. **Build Package**
   - [ ] Clean build artifacts: `rm -rf dist/ build/ *.egg-info`
   - [ ] Build source distribution: `uv build`
   - [ ] Build wheel: `uv build --wheel`
   - [ ] Verify package contents

5. **Test Installation**
   - [ ] Create clean virtual environment
   - [ ] Install from source: `pip install .`
   - [ ] Install from wheel: `pip install dist/*.whl`
   - [ ] Verify CLI works: `pysophos --version`
   - [ ] Test basic functionality

6. **Git Tagging**
   - [ ] Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
   - [ ] Push tag: `git push origin v0.1.0`

7. **PyPI Publication** (when ready)
   - [ ] Create PyPI account (if needed)
   - [ ] Configure API tokens
   - [ ] Upload to TestPyPI first: `twine upload --repository testpypi dist/*`
   - [ ] Test installation from TestPyPI
   - [ ] Upload to PyPI: `twine upload dist/*`
   - [ ] Verify package on PyPI

8. **Post-Release**
   - [ ] Create GitHub release
   - [ ] Update project status
   - [ ] Announce release (if applicable)
   - [ ] Monitor for issues

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Current version: **0.1.0** (Initial release)

## Notes

- This is the initial release (0.1.0)
- All core functionality is implemented
- CLI is fully functional
- Documentation is complete
- Test coverage is at 74%
- Ready for community feedback

