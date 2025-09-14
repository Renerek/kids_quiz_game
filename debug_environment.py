#!/usr/bin/env python3
"""
Debug script to check Python version and environment in CI/CD
"""

import sys
import platform
import os
import subprocess

def main():
    print("=" * 60)
    print("PYTHON ENVIRONMENT DEBUG INFORMATION")
    print("=" * 60)
    
    # Python version information
    print(f"Python version: {sys.version}")
    print(f"Python version info: {sys.version_info}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Environment variables
    print("\n" + "=" * 40)
    print("ENVIRONMENT VARIABLES")
    print("=" * 40)
    
    important_vars = [
        'PYTHON_VERSION', 'PYTHONPATH', 'PATH', 'VIRTUAL_ENV',
        'CI', 'GITLAB_CI', 'CI_PROJECT_DIR', 'CI_COMMIT_REF_NAME'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    # Check available Python versions
    print("\n" + "=" * 40)
    print("AVAILABLE PYTHON VERSIONS")
    print("=" * 40)
    
    python_commands = ['python', 'python3', 'python3.10', 'python3.11', 'python3.12']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"{cmd}: {result.stdout.strip()}")
            else:
                print(f"{cmd}: Not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{cmd}: Not found")
    
    # Check pip version
    print("\n" + "=" * 40)
    print("PIP INFORMATION")
    print("=" * 40)
    
    try:
        import pip
        print(f"Pip version: {pip.__version__}")
    except ImportError:
        print("Pip not available as module")
    
    try:
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"Pip command: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Pip command not found")
    
    # Check Django installation
    print("\n" + "=" * 40)
    print("DJANGO INFORMATION")
    print("=" * 40)
    
    try:
        import django
        print(f"Django version: {django.get_version()}")
        print(f"Django location: {django.__file__}")
    except ImportError:
        print("Django not installed")
    
    # Check if we're in a virtual environment
    print("\n" + "=" * 40)
    print("VIRTUAL ENVIRONMENT")
    print("=" * 40)
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Running in virtual environment")
        print(f"Virtual env prefix: {sys.prefix}")
        if hasattr(sys, 'base_prefix'):
            print(f"Base prefix: {sys.base_prefix}")
    else:
        print("NOT running in virtual environment")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
