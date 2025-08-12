#!/usr/bin/env python3
"""
Test runner script for AINative Python SDK

Runs the complete test suite with coverage reporting and provides
detailed output about test results and coverage.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description=""):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Exit code: {result.returncode}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Run AINative SDK tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print(f"Running tests from: {project_dir}")
    print(f"Python version: {sys.version}")
    
    # Install dependencies if needed
    print("\nInstalling dependencies...")
    install_result = run_command(
        "pip install -e .[dev]", 
        "Installing package in development mode"
    )
    
    if install_result.returncode != 0:
        print("Failed to install dependencies")
        return 1
    
    # Build pytest command
    pytest_cmd_parts = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd_parts.append("-v")
    else:
        pytest_cmd_parts.append("-q")
    
    # Add coverage options (unless disabled)
    if not args.no_coverage:
        pytest_cmd_parts.extend([
            "--cov=ainative",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=90"
        ])
    
    # Add test markers
    marker_conditions = []
    
    if args.fast:
        marker_conditions.append("not slow")
    
    if args.unit_only:
        pytest_cmd_parts.append("tests/unit/")
    elif args.integration_only:
        pytest_cmd_parts.append("tests/integration/")
        marker_conditions.append("integration")
    else:
        pytest_cmd_parts.append("tests/")
    
    # Add marker conditions
    if marker_conditions:
        pytest_cmd_parts.extend(["-m", " and ".join(marker_conditions)])
    
    # Additional pytest options
    pytest_cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--durations=10"  # Show 10 slowest tests
    ])
    
    pytest_cmd = " ".join(pytest_cmd_parts)
    
    # Run tests
    test_result = run_command(pytest_cmd, "Running test suite")
    
    # Generate test summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    if test_result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    # Coverage summary
    if not args.no_coverage and test_result.returncode == 0:
        print("\nCoverage report generated:")
        print(f"  - Terminal: (shown above)")
        print(f"  - HTML: {project_dir}/htmlcov/index.html")
        print(f"  - XML: {project_dir}/coverage.xml")
    
    # Additional information
    print(f"\nTest files location: {project_dir}/tests/")
    print(f"Configuration: {project_dir}/pytest.ini")
    
    return test_result.returncode


if __name__ == "__main__":
    sys.exit(main())