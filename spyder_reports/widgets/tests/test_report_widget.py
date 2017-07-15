# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the reportsgui."""

# Third party imports
import pytest
from qtpy.QtCore import Qt
from qtpy.QtWebEngineWidgets import WEBENGINE

# Spyder-IDE and Local imports
from spyder_reports.widgets.reportsgui import ReportsWidget


def same_html(widget, html):
    """
    Check if certain html content is exactly the same in a
    web widget.
    """
    if WEBENGINE:
        def callback(data):
            global HTML
            HTML = data
        widget.toHtml(callback)
        try:
            return html == HTML
        except NameError:
            return False
    else:
        return html == widget.mainFrame().toHtml()


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


def test_close_tabs(qtbot):
    """Test closing tabs.
    When a tab is closed also the reference to the renderview should be removed.
    """
    reports = setup_reports(qtbot)

    def close_tab(index):
        """Find the close button and click it"""
        for i in [0, 1]:  # LeftSide, RightSide
            close_button = reports.tabs.tabBar().tabButton(index, i)
            if close_button:
                break
        qtbot.mouseClick(close_button, Qt.LeftButton)

    reports.set_html('some html', 'file1')
    reports.set_html('some html', 'file2')
    assert reports.tabs.count() == 2

    # close 'file2'
    close_tab(1)
    assert reports.tabs.count() == 1
    assert reports.renderviews.get('file2') is None

    # close 'file1'
    close_tab(0)
    assert reports.tabs.count() == 0
    assert reports.renderviews.get('file1') is None


def test_set_html(qtbot):
    """Test set html."""
    reports = setup_reports(qtbot)

    html = "<html><head></head><body>some html</body></html>"
    reports.set_html(html, 'file1')

    renderviews = reports.renderviews.get('file1')
    qtbot.waitUntil(lambda: same_html(renderviews.page(), html), timeout=5000)
    assert same_html(renderviews.page(), html)


def test_set_html_from_file(qtbot, tmpdir_factory):
    """Test seting a html from a file."""
    reports = setup_reports(qtbot)

    # Create html file
    html = "<html><head></head><body>some html</body></html>"
    html_file = tmpdir_factory.mktemp('data').join('test_report.html')
    html_file.write(html)

    reports.set_html_from_file(str(html_file))

    renderviews = reports.renderviews.get('test_report.html')
    qtbot.waitUntil(lambda: same_html(renderviews.page(), html), timeout=5000)
    assert same_html(renderviews.page(), html)


if __name__ == "__main__":
    pytest.main()
