#!/usr/bin/env python
"""
Script to run tests with coverage
"""
import subprocess
import sys


def run_tests():
    """Run tests with coverage"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--asyncio-mode=auto"
    ]

    print("Running tests with coverage...")
    print("Command:", " ".join(cmd))
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("Coverage report: htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
