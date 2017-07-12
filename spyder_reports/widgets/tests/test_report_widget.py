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


def test_open_several_tabs(qtbot):
    """Test behaviour when opening several tabs."""
    reports = setup_reports(qtbot)

    reports.set_html('some html', 'file1')
    reports.set_html('some html', 'file2')
    assert reports.tabs.currentIndex() == 1
    assert reports.tabs.count() == 2

    # when re-rendering 'file1' should change to tab 0
    reports.set_html('some html', 'file1')
    assert reports.tabs.currentIndex() == 0

    # It shouldn't open a new tab because the file was already rendered
    assert reports.tabs.count() == 2


if __name__ == "__main__":
    pytest.main()
