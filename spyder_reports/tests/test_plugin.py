# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""

# Third party imports
import pytest

# Spyder-IDE and Local imports
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
    mdw_file = tmpdir_factory.mktemp('data').join('test_report.mdw')
    mdw_file.write('# This is a Markdown report')
    return str(mdw_file)


def test_basic_initialization(qtbot):
    """Test Reports plugin initialization."""
    reports = setup_reports(qtbot)

    # Assert that reports exist
    assert reports is not None


def test_basic_md_render(qtbot, report_mdw_file):
    """Test rendering of an basic .mdw report returning a .html file."""
    reports = setup_reports(qtbot)
    output_file = reports._render_report(report_mdw_file)

    # Assert that output_file is an html file
    assert output_file.split('.')[-1] == 'html'


def test_check_compability(qtbot, monkeypatch):
    """Test state and message returned by check_compatibility."""
    monkeypatch.setattr('spyder_reports.reportsplugin.PYQT4', True)
    monkeypatch.setattr('spyder_reports.reportsplugin.PY3', False)

    reports = setup_reports(qtbot)

    valid, message = reports.check_compatibility()
    assert not valid
    assert 'qt4' in message.lower()
    assert 'python2' in message.lower()


if __name__ == "__main__":
    pytest.main()
