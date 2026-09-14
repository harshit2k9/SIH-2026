"""
Test runner script for SIH-2026 testing suite.
Run this to execute all tests or specific test categories.
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"\n❌ {description} FAILED")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("🚀 SIH-2026 Test Suite Runner")
    print("="*60)

    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed. Install with: pip install pytest pytest-asyncio")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"

    # Test configurations
    test_configs = {
        "all": {
            "cmd": "pytest tests/ -v --tb=short",
            "desc": "Running ALL tests"
        },
        "unit": {
            "cmd": "pytest tests/unit/ -v --tb=short",
            "desc": "Running UNIT tests"
        },
        "integration": {
            "cmd": "pytest tests/integration/ -v --tb=short",
            "desc": "Running INTEGRATION tests"
        },
        "security": {
            "cmd": "pytest tests/security/ -v --tb=short",
            "desc": "Running SECURITY tests"
        },
        "coverage": {
            "cmd": "pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing",
            "desc": "Running tests with COVERAGE"
        },
        "auth": {
            "cmd": "pytest tests/unit/test_auth.py -v --tb=short",
            "desc": "Running AUTHENTICATION tests"
        },
        "audit": {
            "cmd": "pytest tests/unit/test_audit.py -v --tb=short",
            "desc": "Running AUDIT tests"
        },
        "sanitize": {
            "cmd": "pytest tests/unit/test_sanitize.py -v --tb=short",
            "desc": "Running SANITIZATION tests"
        },
    }

    if test_type not in test_configs:
        print(f"\n❌ Unknown test type: {test_type}")
        print("\nAvailable test types:")
        for key in test_configs.keys():
            print(f"  - {key}")
        sys.exit(1)

    config = test_configs[test_type]
    success = run_command(config["cmd"], config["desc"])

    if success:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
