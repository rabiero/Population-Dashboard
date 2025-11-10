#!/usr/bin/env python3
"""
Test runner script for the WorldPop Data Pipeline
"""

import pytest
import sys
import os
from pathlib import Path

def run_all_tests():
    """Run all tests in the tests directory"""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Run pytest with specific options
    pytest_args = [
        str(tests_dir),
        "-v",  # verbose
        "--tb=short",  # short tracebacks
        "-x",  # stop on first failure
        "--log-level=INFO"
    ]
    
    print("Running WorldPop Data Pipeline Tests...")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code

def run_specific_test(test_module):
    """Run a specific test module"""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    test_file = tests_dir / f"test_{test_module}.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    pytest_args = [
        str(test_file),
        "-v",
        "--tb=short"
    ]
    
    print(f"Running {test_module} tests...")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    return exit_code

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run WorldPop Data Pipeline tests')
    parser.add_argument('--module', '-m', type=str, 
                       help='Run specific test module (without test_ prefix)')
    
    args = parser.parse_args()
    
    if args.module:
        exit_code = run_specific_test(args.module)
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)