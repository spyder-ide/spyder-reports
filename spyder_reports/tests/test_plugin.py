# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""

# Third party imports
import pytest
from qtpy.QtWebEngineWidgets import WEBENGINE

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


def test_render_report_thread(qtbot, report_mdw_file):
    """Test rendering report in a worker thread."""
    reports = setup_reports(qtbot)

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        reports.render_report_thread(report_mdw_file)
    
    ok, filename, error = sig.args
    assert ok
    assert error is None

    renderview = reports.report_widget.renderviews.get(filename)
    assert renderview is not None


def test_render_report_thread_error(qtbot):
    """Test rendering report in a worker thread."""
    reports = setup_reports(qtbot)

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        reports.render_report_thread('file_that_doesnt_exist.mdw')

    ok, filename, error = sig.args
    assert not ok
    assert "[Errno 2]" in error
    assert filename is None

    for renderview in reports.report_widget.renderviews:
        assert not 'file_that_doesnt_exist' in renderview


if __name__ == "__main__":
    pytest.main()
