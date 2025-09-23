#!/usr/bin/env python3
"""
Test Runner Script
Run all tests with proper configuration.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🧪 Running Telegram Bot Tests...")
    print("=" * 50)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with coverage
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=modules",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        return False

def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    cmd = ["python", "-m", "pytest", f"tests/{test_file}", "-v", "--tb=short"]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {test_file} passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)
