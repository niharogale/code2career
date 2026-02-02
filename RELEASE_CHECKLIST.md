# AutoDoc Release Checklist

This document provides a checklist for preparing and publishing AutoDoc releases to PyPI.

## ✅ Pre-Release Checklist

### Package Metadata
- [x] Updated `pyproject.toml` with complete metadata
  - [x] Build system configuration (`setuptools`)
  - [x] Project metadata (name, version, description)
  - [x] Python version requirements (>=3.9)
  - [x] License (MIT)
  - [x] Authors and maintainers
  - [x] Keywords and classifiers
  - [x] Dependencies
  - [x] Optional dependencies (dev)
  - [x] Entry points (CLI script)
  - [x] Project URLs (homepage, repository, issues, changelog)
  - [x] Package configuration (setuptools)
  - [x] Tool configurations (pytest, black, ruff, mypy)

### Legal & Contribution
- [x] `LICENSE` - MIT License
- [x] `CONTRIBUTING.md` - Comprehensive contribution guidelines
  - [x] Development setup instructions
  - [x] Code style guidelines
  - [x] Testing requirements
  - [x] Pull request process
  - [x] Commit message conventions

### Documentation
- [x] `README.md` - Professional project README
  - [x] Project overview and features
  - [x] Installation instructions
  - [x] Quick start guide
  - [x] Usage examples
  - [x] Architecture overview
  - [x] Documentation links
  - [x] Contributing section
  - [x] License information
- [x] `CHANGELOG.md` - Version history and release notes
- [x] `docs/API.md` - Complete API documentation
  - [x] All CLI commands with options
  - [x] Core modules documentation
  - [x] Analysis modules documentation
  - [x] Generation modules documentation
  - [x] Exception hierarchy
  - [x] Type definitions
  - [x] Configuration format
  - [x] Code examples
- [x] `docs/EXAMPLES.md` - Practical usage examples
  - [x] Quick start workflow
  - [x] Basic workflows
  - [x] Advanced usage patterns
  - [x] CI/CD integration examples
  - [x] Common patterns
  - [x] Troubleshooting guide
- [x] `docs/README.md` - Documentation index

### Build Configuration
- [x] `MANIFEST.in` - Include/exclude rules for distribution
- [x] `.gitignore` - Updated with build artifacts
- [x] `autodoc/py.typed` - Type checking marker file
- [x] `autodoc/__init__.py` - Version number

### CI/CD
- [x] `.github/workflows/publish.yml` - PyPI publication workflow
  - [x] Build distribution
  - [x] Publish to Test PyPI (manual trigger)
  - [x] Publish to PyPI (on release)
  - [x] Verify installation across Python versions
- [x] `.github/workflows/ci.yml` - Existing CI tests
- [x] `.github/workflows/pr-readme-check.yml` - Existing PR checks
- [x] `.github/workflows/update-readme.yml` - Existing README automation

## 📦 Building the Package

### Local Build

```bash
# Install build tools
pip install build twine

# Build distribution packages
python -m build

# This creates:
# - dist/autodoc-0.1.0.tar.gz (source distribution)
# - dist/autodoc-0.1.0-py3-none-any.whl (wheel distribution)
```

### Verify Distribution

```bash
# Check package metadata
twine check dist/*

# Inspect contents
tar -tzf dist/autodoc-0.1.0.tar.gz | head -20
unzip -l dist/autodoc-0.1.0-py3-none-any.whl
```

## 🧪 Testing the Package

### Test Installation Locally

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install from local build
pip install dist/autodoc-0.1.0-py3-none-any.whl

# Test basic functionality
autodoc --help
autodoc init
autodoc scan
autodoc generate readme --dry-run

# Cleanup
deactivate
rm -rf test-env
```

### Test on Test PyPI

```bash
# Upload to Test PyPI (requires account)
twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    autodoc

# Test functionality
autodoc --help
```

## 🚀 Publishing to PyPI

### Method 1: Manual Upload (Initial Setup)

```bash
# Install twine if not already installed
pip install twine

# Upload to PyPI (requires PyPI account and API token)
twine upload dist/*

# Enter credentials:
# Username: __token__
# Password: pypi-AgEIcH... (your API token)
```

### Method 2: GitHub Actions (Automated)

1. **Set up PyPI API token:**
   - Go to https://pypi.org/manage/account/token/
   - Create new API token with "Entire account" scope
   - Copy the token (starts with `pypi-`)

2. **Configure GitHub Secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add repository secret: `PYPI_API_TOKEN`
   - Paste your PyPI API token

3. **Test with Test PyPI first:**
   - Go to Actions → "Publish to PyPI" workflow
   - Click "Run workflow"
   - Check "Publish to Test PyPI"
   - Verify installation works

4. **Publish via GitHub Release:**
   - Create a new release on GitHub
   - Tag: `v0.1.0`
   - Title: `AutoDoc v0.1.0`
   - Description: Copy from CHANGELOG.md
   - Publish release
   - GitHub Actions will automatically build and publish to PyPI

## 📋 Post-Release Tasks

### Verification

- [ ] Verify package on PyPI: https://pypi.org/project/autodoc/
- [ ] Test installation: `pip install autodoc`
- [ ] Verify documentation renders correctly on PyPI
- [ ] Check all badges work in README
- [ ] Test CLI: `autodoc --help`

### Announcement

- [ ] Update project README badges
- [ ] Tweet/social media announcement
- [ ] Share on Reddit (r/Python)
- [ ] Post on Hacker News
- [ ] Update personal portfolio
- [ ] Notify contributors

### Monitoring

- [ ] Monitor PyPI download statistics
- [ ] Watch for issues on GitHub
- [ ] Respond to user feedback
- [ ] Track feature requests

## 🔄 Version Bumping for Future Releases

### 1. Update Version Number

**In `pyproject.toml`:**
```toml
version = "0.2.0"  # Increment version
```

**In `autodoc/__init__.py`:**
```python
__version__ = "0.2.0"
```

### 2. Update CHANGELOG.md

Add new version section:
```markdown
## [0.2.0] - 2026-XX-XX

### Added
- New feature descriptions

### Changed
- Modified functionality

### Fixed
- Bug fixes
```

### 3. Commit and Tag

```bash
git add pyproject.toml autodoc/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags
```

### 4. Create GitHub Release

- Go to GitHub → Releases → Draft a new release
- Select tag: `v0.2.0`
- Release title: `AutoDoc v0.2.0`
- Description: Copy from CHANGELOG.md
- Publish release (triggers PyPI publication)

## 🐛 Troubleshooting

### Build Fails

**Issue:** `python -m build` fails

**Solutions:**
- Ensure `setuptools` and `wheel` are installed: `pip install setuptools wheel`
- Check `pyproject.toml` syntax
- Verify all files in `MANIFEST.in` exist

### Upload Fails

**Issue:** `twine upload` fails with authentication error

**Solutions:**
- Verify PyPI account is verified (email confirmation)
- Use API token instead of password
- Format: Username: `__token__`, Password: `pypi-...`
- Check token has correct scope

### Package Import Fails

**Issue:** After installation, `import autodoc` fails

**Solutions:**
- Check `pyproject.toml` `[tool.setuptools.packages.find]` configuration
- Ensure `autodoc/__init__.py` exists
- Verify package structure with `pip show -f autodoc`

### Missing Dependencies

**Issue:** Package installs but dependencies are missing

**Solutions:**
- Check `dependencies` list in `pyproject.toml`
- Use `pip install -e ".[dev]"` for development dependencies
- Test installation in clean environment

## 📚 Resources

### PyPI Documentation
- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)

### GitHub Actions
- [PyPI Publish Action](https://github.com/marketplace/actions/pypi-publish)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

### Semantic Versioning
- [SemVer Specification](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

## ✅ Current Status

**Package:** Ready for publication ✅

All prerequisites completed:
- ✅ Package metadata (pyproject.toml)
- ✅ Legal files (LICENSE)
- ✅ Documentation (README, CONTRIBUTING, API, EXAMPLES)
- ✅ Build configuration (MANIFEST.in, py.typed)
- ✅ CI/CD workflows (publish.yml)
- ✅ Version tracking (CHANGELOG.md)

**Next Steps:**
1. Build package: `python -m build`
2. Test on Test PyPI: Manual workflow trigger
3. Create GitHub release: `v0.1.0`
4. Package automatically publishes to PyPI

---

**Note:** This checklist should be reviewed and updated with each release to ensure all steps are followed.
