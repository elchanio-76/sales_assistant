"""
Shared pytest fixtures for all tests.

This file contains common fixtures that can be used across all test modules.
"""

import pytest
import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


@pytest.fixture(scope="session")
def app_root():
    """Return the application root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory."""
    data_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
