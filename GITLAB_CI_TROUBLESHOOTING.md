# GitLab CI/CD Troubleshooting Guide

## Problem: Python Version Conflicts (3.1 vs 3.10)

### Common Causes & Solutions

#### 1. **Incorrect Docker Image**
**Problem**: GitLab CI using old Docker image with Python 3.1
**Solution**: Explicitly specify Python version in `.gitlab-ci.yml`

```yaml
# ✅ CORRECT - Use specific Python version
test:
  image: python:3.12-slim  # or python:3.10-slim

# ❌ WRONG - Generic image may use old Python
test:
  image: ubuntu:latest
```

#### 2. **Missing Python Version Specification**
**Problem**: CI defaults to system Python
**Solution**: Add explicit version control files

Files created to fix this:
- ✅ `.gitlab-ci.yml` - Specifies `python:3.12-slim`
- ✅ `runtime.txt` - Contains `python-3.12.11`
- ✅ `pyproject.toml` - Requires `>=3.10`

#### 3. **Cache Issues**
**Problem**: Old Python version cached
**Solution**: Clear GitLab CI cache

```yaml
# Add to your GitLab CI job
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .cache/pip/
    - .venv/
```

#### 4. **Virtual Environment Issues**
**Problem**: Wrong Python used for venv
**Solution**: Use explicit python3 commands

```yaml
before_script:
  - python3 --version  # Debug: show version
  - python3 -m venv .venv
  - source .venv/bin/activate
  - python --version   # Should now show correct version
```

## Quick Fixes to Try

### 1. **Update GitLab CI Configuration**
Replace your current `.gitlab-ci.yml` with the one provided, which includes:
- Explicit Python 3.12 Docker image
- Proper virtual environment setup
- Version debugging commands

### 2. **Add Version Control Files**
Ensure these files exist (already created for you):
- `runtime.txt` - Platform-specific version
- `pyproject.toml` - Python requirements
- `requirements.txt` - Dependencies

### 3. **Clear GitLab CI Cache**
In GitLab web interface:
1. Go to your project
2. Navigate to CI/CD → Pipelines
3. Click "Clear Runner Caches"

### 4. **Debug in CI**
Add this to your `.gitlab-ci.yml` for debugging:

```yaml
debug_environment:
  stage: test
  image: python:3.12-slim
  script:
    - python3 debug_environment.py
  when: manual
```

## Verification Steps

### 1. **Local Testing**
Test the CI configuration locally:

```bash
# Use the same commands as CI
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py test
```

### 2. **GitLab CI Variables**
Check GitLab project settings:
- Go to Settings → CI/CD → Variables
- Ensure no conflicting `PYTHON_VERSION` variables

### 3. **Runner Configuration**
If using custom GitLab runners:
- Ensure runners have Python 3.10+ installed
- Update runner configuration if needed

## Alternative Solutions

### Option 1: Use conda instead of pip
```yaml
before_script:
  - conda create -n myenv python=3.12
  - conda activate myenv
  - pip install -r requirements.txt
```

### Option 2: Use pyenv for version management
```yaml
before_script:
  - pyenv install 3.12.11
  - pyenv global 3.12.11
  - python --version
```

### Option 3: Use Docker multi-stage build
```yaml
test:
  image: 
    name: python:3.12-slim
    entrypoint: [""]
```

## Files Modified/Created

### ✅ `.gitlab-ci.yml`
- Uses `python:3.12-slim` image
- Explicit version commands
- Proper virtual environment setup
- Cache configuration

### ✅ `pyproject.toml`
- Requires Python >= 3.10
- Explicit version classifiers
- Development dependencies

### ✅ `runtime.txt`
- Specifies exact Python version
- Used by some deployment platforms

### ✅ `requirements-dev.txt`
- Development-specific dependencies
- Testing and linting tools

### ✅ `debug_environment.py`
- Debug script to check Python environment
- Run manually in CI for troubleshooting

## Testing the Fix

1. **Commit and push** the new configuration files
2. **Monitor the pipeline** in GitLab
3. **Check the logs** for Python version confirmation
4. **Run the debug script** if issues persist

## Expected GitLab CI Output

After the fix, you should see:
```
Python version being used:
Python 3.12.11 (main, ...)
Installing dependencies...
Successfully installed Django-5.2.6 ...
Running Django tests...
...
```

## Still Having Issues?

If problems persist:

1. **Check GitLab Runner logs** for more details
2. **Verify Docker image availability** on GitLab
3. **Contact GitLab support** if using GitLab.com
4. **Try a different Python version** (3.10, 3.11) if 3.12 has issues

The configuration provided should resolve the Python 3.1 vs 3.10+ conflict by explicitly controlling the Python version throughout the CI/CD pipeline.
