# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""

# Test library imports
import pytest

# Local imports
from spyder_reports.reportsplugin import ReportsPlugin


@pytest.fixture
def setup_reports(qtbot):
    """Set up the Reports plugin."""
    reports = ReportsPlugin(None)
    qtbot.addWidget(reports)
    reports.show()
    return reports


def test_basic_initialization(qtbot):
    """Test Reports plugin initialization."""
    reports = setup_reports(qtbot)

    # Assert that reports exist
    assert reports is not None


if __name__ == "__main__":
    pytest.main()
