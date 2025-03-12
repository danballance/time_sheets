"""
Pytest configuration for time_sheets tests.

This file contains shared fixtures and configuration for the test suite.
"""

import pytest
from time_sheets import TimeSheetGenerator


@pytest.fixture
def generator():
    """Fixture to create a TimeSheetGenerator instance for tests."""
    return TimeSheetGenerator()
