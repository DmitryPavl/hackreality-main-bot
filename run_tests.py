#!/usr/bin/env python3
"""
Test runner script for HackReality Bot
"""
import sys
import subprocess
import os

def run_tests():
    """Run the test suite with coverage reporting."""
    print("🧪 Running HackReality Bot Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("❌ Error: tests directory not found. Please run from project root.")
        sys.exit(1)
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], 
                      check=True, capture_output=True)
        print("✅ Test dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        sys.exit(1)
    
    # Run tests with coverage
    print("\n🔍 Running tests with coverage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--cov=modules", 
            "--cov=main", 
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ], check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
