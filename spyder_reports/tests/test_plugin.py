# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""

# Third party imports
import pytest
import os.path as osp

# Spyder-IDE and Local imports
from spyder.utils.programs import TEMPDIR
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
    assert osp.exists(filename)

    renderview = reports.report_widget.renderviews.get(report_mdw_file)
    assert renderview is not None


def test_render_report_thread_error(qtbot):
    """Test rendering report in a worker thread."""
    reports = setup_reports(qtbot)

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        reports.render_report_thread('file_that_doesnt_exist.mdw')

    ok, filename, error = sig.args
    assert not ok
    assert "[Errno 2]" in error
    assert filename == 'file_that_doesnt_exist.mdw'

    def tab_closed():
        assert reports.report_widget.tabs.count() == 0

    qtbot.waitUntil(tab_closed)
    for renderview in reports.report_widget.renderviews:
        assert 'file_that_doesnt_exist' not in renderview


def test_render_tmp_dir(qtbot, report_mdw_file):
    """Test that rendered files are created in spyder's tempdir."""
    reports = setup_reports(qtbot)
    output_file = reports._render_report(report_mdw_file)

    # Test that outfile is in spyder tmp dir
    assert osp.samefile(osp.commonprefix([output_file, TEMPDIR]), TEMPDIR)


def test_render_same_file(qtbot, report_mdw_file):
    """Test that re-rendered files are created in the same tempdir."""
    reports = setup_reports(qtbot)

    output_file1 = reports._render_report(report_mdw_file)
    output_file2 = reports._render_report(report_mdw_file)

    assert osp.exists(output_file2)
    # Assert that file has been re-rendered in the same path
    assert osp.samefile(output_file1, output_file2)


if __name__ == "__main__":
    pytest.main()
