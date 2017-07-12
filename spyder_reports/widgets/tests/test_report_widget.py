# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the reportsgui."""

# Third party imports
import pytest

# Spyder-IDE and Local imports
from spyder_reports.widgets.reportsgui import ReportsWidget


@pytest.fixture
def setup_reports(qtbot):
    """Set up reports."""
    widget = ReportsWidget(None)
    qtbot.addWidget(widget)
    return widget


def test_reports(qtbot):
    """Run Reports Widget."""
    reports = setup_reports(qtbot)
    assert reports


def test_overwrite_welcome(qtbot):
    """Test taht the first rendering doesn't create a new tab.
    It should overwrite 'Welcome' tab instead.
    """
    reports = setup_reports(qtbot)

    renderview = reports.renderviews['Welcome']
    reports.set_html('some html', 'file name')

    assert reports.tabs.count() == 1
    assert len(reports.renderviews) == 1
    assert reports.renderviews['file name'] == renderview


if __name__ == "__main__":
    pytest.main()
