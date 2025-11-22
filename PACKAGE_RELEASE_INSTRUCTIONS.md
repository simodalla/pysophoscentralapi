# Package Release Instructions - PySophosCentralApi v0.1.0

This document provides step-by-step instructions for preparing and releasing version 0.1.0 of PySophosCentralApi.

---

## ✅ Pre-Release Checklist

### Completed
- [x] All tests passing (323 tests, 75% coverage)
- [x] Code quality checks passing (ruff, mypy)
- [x] Documentation complete
- [x] CLI fully functional
- [x] Release notes created

### To Complete
- [ ] Update package metadata (author information)
- [ ] Build and test package
- [ ] Create git release tag
- [ ] (Optional) Publish to PyPI

---

## 📝 Step 1: Update Package Metadata

Edit `pyproject.toml` and update the following fields with your information:

```toml
[project]
authors = [
    {name = "Your Name", email = "your.email@example.com"}  # ← UPDATE THIS
]

[project.urls]
Homepage = "https://github.com/yourusername/pysophoscentralapi"  # ← UPDATE THIS
Documentation = "https://pysophoscentralapi.readthedocs.io"      # ← UPDATE THIS (or remove)
Repository = "https://github.com/yourusername/pysophoscentralapi" # ← UPDATE THIS
Issues = "https://github.com/yourusername/pysophoscentralapi/issues" # ← UPDATE THIS
```

**Replace:**
- `Your Name` with your actual name
- `your.email@example.com` with your email
- `yourusername` with your GitHub username
- Update or remove Documentation URL if not using ReadTheDocs

---

## 🔨 Step 2: Build the Package

### 2.1 Clean Previous Builds

```bash
cd /Users/simo/Projects/pysophoscentralapi
rm -rf dist/ build/ *.egg-info
```

### 2.2 Build Package

```bash
# Install build tools if needed
uv pip install build twine

# Build both sdist and wheel
python -m build
```

This will create:
- `dist/pysophoscentralapi-0.1.0.tar.gz` (source distribution)
- `dist/pysophoscentralapi-0.1.0-py3-none-any.whl` (wheel)

### 2.3 Verify Package Contents

```bash
# List contents of the wheel
unzip -l dist/pysophoscentralapi-0.1.0-py3-none-any.whl

# Check package metadata
tar -tzf dist/pysophoscentralapi-0.1.0.tar.gz | head -20
```

**Verify the package includes:**
- All source files in `pysophoscentralapi/`
- `README.md`, `LICENSE`
- `py.typed` file for type hints
- No test files or unnecessary files

---

## 🧪 Step 3: Test Installation in Clean Environment

### 3.1 Create Test Virtual Environment

```bash
# Create a new test directory
cd ~
mkdir pysophos-test
cd pysophos-test

# Create and activate virtual environment
python3 -m venv test-env
source test-env/bin/activate
```

### 3.2 Install from Local Wheel

```bash
# Install from the wheel you built
pip install /Users/simo/Projects/pysophoscentralapi/dist/pysophoscentralapi-0.1.0-py3-none-any.whl
```

### 3.3 Test the Installation

```bash
# Test CLI is available
pysophos --version

# Test CLI help
pysophos --help

# Test Python import
python -c "from pysophoscentralapi import EndpointAPI; print('Import successful!')"

# Test async import
python -c "from pysophoscentralapi.sync import EndpointAPISync; print('Sync import successful!')"
```

### 3.4 Test with Real Configuration (Optional)

```bash
# If you have a config file, test real commands
pysophos --config-file ~/.pysophos_config.toml config test
pysophos --config-file ~/.pysophos_config.toml endpoint list --limit 5
```

### 3.5 Cleanup

```bash
# Deactivate and remove test environment
deactivate
cd ~
rm -rf pysophos-test
```

---

## 🏷️ Step 4: Create Git Release Tag

### 4.1 Commit All Changes

```bash
cd /Users/simo/Projects/pysophoscentralapi

# Check status
git status

# Add any remaining changes
git add .
git commit -m "chore: prepare release v0.1.0"
```

### 4.2 Create and Push Tag

```bash
# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release

- Complete Endpoint API v1 implementation
- Complete Common API v1 implementation
- Professional CLI with multiple output formats
- Async-first architecture with sync wrappers
- 323 tests passing with 75% coverage"

# Push tag to remote
git push origin v0.1.0

# Push commits
git push
```

---

## 📦 Step 5: Publish to PyPI (Optional)

⚠️ **Important**: Only do this when you're ready to make the package publicly available!

### 5.1 Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Enter your TestPyPI credentials when prompted
```

Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ pysophoscentralapi
```

### 5.2 Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Enter your PyPI credentials when prompted
```

### 5.3 Verify on PyPI

Visit: https://pypi.org/project/pysophoscentralapi/

Test installation:
```bash
pip install pysophoscentralapi
```

---

## 📢 Step 6: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Select tag `v0.1.0`
4. Title: "v0.1.0 - Initial Release"
5. Description: Copy content from `RELEASE_NOTES_v0.1.0.md`
6. Attach the wheel and source distribution files
7. Click "Publish release"

---

## 📝 Step 7: Update Documentation

### Update README badges (if using)
```markdown
[![PyPI version](https://badge.fury.io/py/pysophoscentralapi.svg)](https://badge.fury.io/py/pysophoscentralapi)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### Update project-plan.md
Mark Phase 10 as complete

---

## 🎉 Post-Release Tasks

### Immediate
- [ ] Announce on social media (if desired)
- [ ] Update project status in README
- [ ] Monitor for issues in first 24 hours

### Within a Week
- [ ] Respond to any issues or questions
- [ ] Start planning v0.2.0 features
- [ ] Gather community feedback

---

## 🆘 Troubleshooting

### Build Fails
```bash
# Check for missing files
ls -la src/pysophoscentralapi/

# Verify pyproject.toml syntax
python -m build --help
```

### Import Fails After Installation
```bash
# Check installed packages
pip list | grep pysophos

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall
pip uninstall pysophoscentralapi
pip install pysophoscentralapi
```

### PyPI Upload Fails
```bash
# Check twine
python -m twine check dist/*

# Verify credentials
python -m twine upload --repository testpypi dist/* --verbose
```

---

## 📞 Need Help?

- Check build logs carefully
- Verify all paths are correct
- Test in clean environment
- Check PyPI documentation: https://packaging.python.org/

---

**Good luck with your release! 🚀**


