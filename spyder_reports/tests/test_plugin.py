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


@pytest.fixture(scope='session')
def report_mdw_file(tmpdir_factory):
    """
    Fixture for create a temporary report file (mdw).

    Returns:
        str: Path of temporary mdw file.
    """
    p = tmpdir_factory.mktemp('data').join('test_report.mdw')
    p.write('# This is a Markdown report')
    return str(p)


def test_basic_initialization(qtbot):
    """Test Reports plugin initialization."""
    reports = setup_reports(qtbot)

    # Assert that reports exist
    assert reports is not None


def test_basic_md_render(qtbot, report_mdw_file):
    """Test rendering of an basic .mdw report returning a .html file."""
    reports = setup_reports(qtbot)
    output_file = reports.render_report(report_mdw_file)

    # Assert that output_file is an html file
    assert output_file.split('.')[-1] == 'html'


if __name__ == "__main__":
    pytest.main()
